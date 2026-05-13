"""Тесты PostgreSQL.

Проверяет:
- Наличие методов менеджера БД
- Корректность SQLAlchemy моделей
- Структуру возвращаемой статистики
"""
import pytest
from unittest.mock import patch, MagicMock
from src.database.db_manager import DatabaseManager
from src.database.models import Study, DicomFile, InferenceResult


class TestDatabaseManager:
    
    def test_connection_check(self):
        db_manager = DatabaseManager(auto_init=False)
        assert hasattr(db_manager, 'check_connection')
    
    def test_create_study_method(self):
        db_manager = DatabaseManager(auto_init=False)
        assert hasattr(db_manager, 'create_study')
    
    def test_save_inference_result_method(self):
        db_manager = DatabaseManager(auto_init=False)
        assert hasattr(db_manager, 'save_inference_result')
    
    def test_get_statistics_method(self):
        db_manager = DatabaseManager(auto_init=False)
        assert hasattr(db_manager, 'get_statistics')
    
    def test_get_statistics_returns_dict(self):
        db_manager = DatabaseManager(auto_init=False)
        stats = db_manager.get_statistics()
        assert isinstance(stats, dict)
        assert 'total_studies' in stats
        assert 'total_inferences' in stats
        assert 'avg_left_score' in stats
        assert 'avg_right_score' in stats
        assert 'high_risk_count' in stats
        assert 'high_risk_percentage' in stats


class TestModels:
    
    def test_study_model(self):
        study = Study(
            study_id="TEST-001",
            description="Тестовое исследование"
        )
        assert study.study_id == "TEST-001"
        assert study.description == "Тестовое исследование"
        assert hasattr(study, 'id')
        assert hasattr(study, 'created_at')
        assert hasattr(study, 'updated_at')
    
    def test_dicom_file_model(self):
        dicom_file = DicomFile(
            study_id=1,
            file_path="/test/path.dcm",
            file_name="test.dcm",
            artery_classification="left",
            artery_probability=0.95
        )
        assert dicom_file.file_name == "test.dcm"
        assert dicom_file.artery_classification == "left"
        assert dicom_file.artery_probability == 0.95
    
    def test_inference_result_model(self):
        result = InferenceResult(
            study_id=1,
            left_score=10.5,
            right_score=5.2,
            total_score=15.7,
            is_high_risk=False
        )
        assert result.left_score == 10.5
        assert result.total_score == 15.7
        assert result.is_high_risk is False
        assert hasattr(result, 'inference_date')