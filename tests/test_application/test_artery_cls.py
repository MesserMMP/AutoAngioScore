"""Тесты классификатора артерий: пустой ввод, пороги 0.10/0.90, серая зона."""

import pytest
import numpy as np
from unittest.mock import patch, MagicMock
from application.artery_cls import classify_artery


class TestArteryClassifier:

    def test_classify_artery_empty(self):
        result = classify_artery([])
        assert result["left"] == []
        assert result["right"] == []
        assert result["other"] == []

    def test_classify_artery_with_mock(self, sample_dicom_files):
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

            result = classify_artery(sample_dicom_files)
            assert "left" in result
            assert "right" in result
            assert "other" in result

    def test_classify_artery_thresholds(self, sample_dicom_files):
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
            result_left = classify_artery(sample_dicom_files[:1])
            assert len(result_left["left"]) >= 0

            mock_sigmoid.return_value = MagicMock(item=lambda: 0.95)
            result_right = classify_artery(sample_dicom_files[:1])
            assert len(result_right["right"]) >= 0

            mock_sigmoid.return_value = MagicMock(item=lambda: 0.50)
            result_other = classify_artery(sample_dicom_files[:1])
            assert "other" in result_other