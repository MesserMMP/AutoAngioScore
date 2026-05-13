"""Тесты работы с DICOM файлами.

Проверяет:
- Валидацию DICOM файлов (расширение, чтение pydicom)
- Конвертацию загруженных файлов в пути
- Сбор путей из разных источников с устранением дубликатов
"""
import os
from pathlib import Path
import pytest
from unittest.mock import patch, MagicMock
from src.web.files import is_dicom_path, files_to_paths, collect_input_paths
from tests.conftest import MockFile


class TestFileValidation:
    
    def test_is_dicom_path_valid_with_mock(self, sample_dicom_files):
        with patch('src.web.files.pydicom.dcmread') as mock_dcmread:
            mock_dcmread.return_value = MagicMock()
            for file_path in sample_dicom_files:
                result = is_dicom_path(file_path)
                assert result is True
    
    def test_is_dicom_path_invalid_extension(self, temp_dir):
        invalid_path = os.path.join(temp_dir, "test.txt")
        with open(invalid_path, 'w') as f:
            f.write("test")
        result = is_dicom_path(invalid_path)
        assert result is False
    
    def test_is_dicom_path_nonexistent(self):
        result = is_dicom_path("/nonexistent/file.dcm")
        assert result is False
    
    def test_is_dicom_path_with_pydicom_error(self, temp_dir):
        file_path = os.path.join(temp_dir, "corrupt.dcm")
        Path(file_path).touch()
        
        with patch('src.web.files.pydicom.dcmread') as mock_dcmread:
            mock_dcmread.side_effect = Exception("Invalid DICOM")
            result = is_dicom_path(file_path)
            assert result is False


class TestFilesToPaths:
    
    def test_files_to_paths_empty(self):
        result = files_to_paths(None)
        assert result == []
        
        result = files_to_paths([])
        assert result == []
    
    def test_files_to_paths_valid(self, sample_dicom_files):
        with patch('src.web.files.pydicom.dcmread') as mock_dcmread:
            mock_dcmread.return_value = MagicMock()
            mock_files = [MockFile(path) for path in sample_dicom_files]
            paths = files_to_paths(mock_files)
            assert len(paths) == len(sample_dicom_files)
            for path in paths:
                assert path in sample_dicom_files
    
    def test_files_to_paths_with_invalid(self, sample_dicom_files, sample_invalid_files):
        with patch('src.web.files.pydicom.dcmread') as mock_dcmread:
            mock_dcmread.return_value = MagicMock()
            all_files = sample_dicom_files + sample_invalid_files
            mock_files = [MockFile(path) for path in all_files]
            paths = files_to_paths(mock_files)
            assert len(paths) == len(sample_dicom_files)


class TestCollectInputPaths:
    
    def test_collect_input_paths_empty(self):
        paths = collect_input_paths(None, None)
        assert paths == []
    
    def test_collect_input_paths_only_files(self, sample_dicom_files):
        with patch('src.web.files.pydicom.dcmread') as mock_dcmread:
            mock_dcmread.return_value = MagicMock()
            mock_files = [MockFile(path) for path in sample_dicom_files]
            paths = collect_input_paths(mock_files, None)
            assert len(paths) == len(sample_dicom_files)
    
    def test_collect_input_paths_only_folder(self, sample_dicom_files):
        with patch('src.web.files.pydicom.dcmread') as mock_dcmread:
            mock_dcmread.return_value = MagicMock()
            mock_folder = [MockFile(path) for path in sample_dicom_files]
            paths = collect_input_paths(None, mock_folder)
            assert len(paths) == len(sample_dicom_files)
    
    def test_collect_input_paths_duplicates(self, sample_dicom_files):
        with patch('src.web.files.pydicom.dcmread') as mock_dcmread:
            mock_dcmread.return_value = MagicMock()
            mock_files = [MockFile(path) for path in sample_dicom_files]
            mock_folder = [MockFile(path) for path in sample_dicom_files]
            paths = collect_input_paths(mock_files, mock_folder)
            assert len(paths) == len(sample_dicom_files)