"""Тесты ML инференса.

Проверяет:
- Фильтрацию и сортировку DICOM путей
- Создание объектов Study
- Инференс с моками моделей и без моделей
"""
import pytest
from unittest.mock import patch, MagicMock
import numpy as np
from src.syntax_pred.infer import Study, run_inference, _filter_dicom_paths, _stable_sort_paths


class TestInferenceHelpers:
    
    def test_filter_dicom_paths_empty(self):
        result = _filter_dicom_paths([])
        assert result == []
    
    def test_filter_dicom_paths_with_mock(self, sample_dicom_files):
        with patch('src.syntax_pred.infer.pydicom.dcmread') as mock_dcmread:
            mock_dcmread.return_value = MagicMock()
            result = _filter_dicom_paths(sample_dicom_files)
            assert len(result) == len(sample_dicom_files)
    
    def test_filter_dicom_paths_with_invalid(self, sample_invalid_files):
        with patch('src.syntax_pred.infer.pydicom.dcmread') as mock_dcmread:
            mock_dcmread.side_effect = Exception("Invalid DICOM")
            result = _filter_dicom_paths(sample_invalid_files)
            assert result == []
    
    def test_stable_sort_paths_empty(self):
        result = _stable_sort_paths([])
        assert result == []
    
    def test_stable_sort_paths_with_mock(self, sample_dicom_files):
        with patch('src.syntax_pred.infer.pydicom.dcmread') as mock_dcmread:
            mock_instance = MagicMock()
            mock_instance.SeriesInstanceUID = "test-series"
            mock_dcmread.return_value = mock_instance
            
            result = _stable_sort_paths(sample_dicom_files)
            assert len(result) == len(sample_dicom_files)
    
    def test_stable_sort_paths_duplicates(self, sample_dicom_files):
        paths = sample_dicom_files + sample_dicom_files
        result = _stable_sort_paths(paths)
        assert len(result) == len(paths)


class TestStudyClass:
    
    def test_study_creation(self, sample_dicom_files):
        study = Study(
            name="TEST-001",
            description="Описание",
            files=sample_dicom_files
        )
        assert study.name == "TEST-001"
        assert study.description == "Описание"
        assert len(study.files) == len(sample_dicom_files)
    
    def test_study_empty_description(self, sample_dicom_files):
        study = Study(
            name="TEST-001",
            description="",
            files=sample_dicom_files
        )
        assert study.description == ""


class TestRunInference:
    
    def test_run_inference_empty(self):
        result = run_inference([])
        assert "studies" in result
        assert result["studies"] == []
    
    def test_run_inference_with_mock_models(self, sample_study):
        with patch('src.syntax_pred.infer._LEFT_MODELS', [MagicMock()]), \
             patch('src.syntax_pred.infer._RIGHT_MODELS', [MagicMock()]), \
             patch('src.syntax_pred.infer.classify_artery') as mock_classify, \
             patch('src.syntax_pred.infer._score_side_by_models') as mock_score, \
             patch('src.syntax_pred.infer.pydicom.dcmread') as mock_dcmread:
            
            mock_ds = MagicMock()
            mock_ds.pixel_array = np.zeros((32, 512, 512), dtype=np.uint8)
            mock_dcmread.return_value = mock_ds
            
            mock_classify.return_value = {
                "left": [{"path": "test.dcm", "artery_prob": 0.05}],
                "right": [{"path": "test.dcm", "artery_prob": 0.95}],
                "other": []
            }
            mock_score.return_value = {"mean": 10.0, "per_model": [], "n_files": 1}
            
            result = run_inference([sample_study])
            assert "studies" in result
    
    def test_run_inference_no_models(self, sample_study):
        with patch('src.syntax_pred.infer._LEFT_MODELS', []), \
             patch('src.syntax_pred.infer._RIGHT_MODELS', []):
            result = run_inference([sample_study])
            assert "error" in result