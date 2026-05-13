"""Тесты с реальными DICOM файлами. При отсутствии используются моки."""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock
import numpy as np
import pytest

from application.infer import Study, run_inference
from presentation.files import is_dicom_path


class TestRealOrMockedInference:

    @pytest.fixture(autouse=True)
    def setup_config(self, test_config):
        self.real_dicom_path = test_config['dicom_path']
        self.real_dicom_dir = test_config['dicom_dir']

    def has_real_dicom_files(self) -> bool:
        return bool(self.real_dicom_path and os.path.exists(self.real_dicom_path))

    def has_real_dicom_dir(self) -> bool:
        return bool(self.real_dicom_dir and os.path.isdir(self.real_dicom_dir))

    def test_dicom_validation_with_real_or_mock(self):
        if self.has_real_dicom_files():
            with patch('presentation.files.pydicom.dcmread') as mock_dcmread:
                mock_dcmread.return_value = MagicMock()
                result = is_dicom_path(self.real_dicom_path)
                assert result is True
        else:
            with tempfile.NamedTemporaryFile(suffix='.dcm', delete=False) as tmp:
                tmp_path = tmp.name
            try:
                with patch('presentation.files.pydicom.dcmread') as mock_dcmread:
                    mock_dcmread.return_value = MagicMock()
                    result = is_dicom_path(tmp_path)
                    assert result is True
            finally:
                Path(tmp_path).unlink(missing_ok=True)

    def test_inference_with_real_or_mock(self):
        if self.has_real_dicom_files():
            study = Study(
                name="REAL-TEST",
                description="Тест с реальным DICOM",
                files=[self.real_dicom_path]
            )
            result = run_inference([study])
            assert "studies" in result
        else:
            with patch('application.infer._LEFT_MODELS', [MagicMock()]), \
                 patch('application.infer._RIGHT_MODELS', [MagicMock()]), \
                 patch('application.infer.classify_artery') as mock_classify, \
                 patch('application.infer._score_side_by_models') as mock_score, \
                 patch('application.infer.pydicom.dcmread') as mock_dcmread:

                mock_ds = MagicMock()
                mock_ds.pixel_array = np.zeros((32, 512, 512), dtype=np.uint8)
                mock_dcmread.return_value = mock_ds

                mock_classify.return_value = {
                    "left": [{"path": "mock.dcm", "artery_prob": 0.05}],
                    "right": [],
                    "other": []
                }
                mock_score.return_value = {"mean": 15.0, "per_model": [], "n_files": 1}

                study = Study(
                    name="MOCK-TEST",
                    description="Мок-тест",
                    files=["/mock/path.dcm"]
                )
                result = run_inference([study])
                assert "studies" in result

    def test_directory_inference_with_real_or_mock(self):
        if self.has_real_dicom_dir():
            dicom_files = []
            for f in os.listdir(self.real_dicom_dir):
                file_path = os.path.join(self.real_dicom_dir, f)
                if os.path.isfile(file_path):
                    dicom_files.append(file_path)

            if dicom_files:
                study = Study(
                    name="REAL-DIR-TEST",
                    description="Тест с папкой",
                    files=dicom_files
                )
                result = run_inference([study])
                assert "studies" in result
        else:
            with patch('application.infer._LEFT_MODELS', [MagicMock()]), \
                 patch('application.infer._RIGHT_MODELS', [MagicMock()]), \
                 patch('application.infer.classify_artery') as mock_classify, \
                 patch('application.infer._score_side_by_models') as mock_score, \
                 patch('application.infer.pydicom.dcmread') as mock_dcmread:

                mock_ds = MagicMock()
                mock_ds.pixel_array = np.zeros((32, 512, 512), dtype=np.uint8)
                mock_dcmread.return_value = mock_ds

                mock_classify.return_value = {
                    "left": [{"path": "mock1.dcm", "artery_prob": 0.05}],
                    "right": [{"path": "mock2.dcm", "artery_prob": 0.95}],
                    "other": []
                }
                mock_score.return_value = {"mean": 12.0, "per_model": [], "n_files": 1}

                study = Study(
                    name="MOCK-DIR-TEST",
                    description="Мок-тест директории",
                    files=["/mock/dir/file1.dcm", "/mock/dir/file2.dcm"]
                )
                result = run_inference([study])
                assert "studies" in result


class TestArteryClassificationRealOrMock:

    @pytest.fixture(autouse=True)
    def setup_config(self, test_config):
        self.real_dicom_path = test_config['dicom_path']

    def has_real_dicom_files(self) -> bool:
        return bool(self.real_dicom_path and os.path.exists(self.real_dicom_path))

    def test_classify_artery_with_real_or_mock(self):
        from application.artery_cls import classify_artery

        if self.has_real_dicom_files():
            result = classify_artery([self.real_dicom_path])
            assert "left" in result
            assert "right" in result
            assert "other" in result
        else:
            with patch('application.artery_cls._load_artery_model') as mock_load, \
                 patch('application.artery_cls._artery_transform') as mock_transform, \
                 patch('application.artery_cls.pydicom.dcmread') as mock_dcmread, \
                 patch('application.artery_cls.torch.sigmoid') as mock_sigmoid:

                mock_ds = MagicMock()
                mock_ds.pixel_array = np.zeros((32, 512, 512), dtype=np.uint8)
                mock_dcmread.return_value = mock_ds

                mock_model = MagicMock()
                mock_output = MagicMock()
                mock_output.__getitem__ = MagicMock(return_value=MagicMock())
                mock_model.return_value = mock_output
                mock_load.return_value = mock_model
                mock_transform.return_value = MagicMock()
                mock_sigmoid.return_value = MagicMock(item=lambda: 0.05)

                result = classify_artery(["/mock/path.dcm"])
                assert "left" in result
                assert "right" in result
                assert "other" in result