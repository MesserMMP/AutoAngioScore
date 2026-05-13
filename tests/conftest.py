"""Фикстуры для тестов AutoAngioScore: временные директории, моки, тестовые данные."""

import os
import sys
import pytest
import tempfile
from pathlib import Path
from typing import List, Dict, Any
from unittest.mock import Mock, MagicMock
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from application.infer import Study

load_dotenv('.env.test')
if not os.getenv('TEST_DICOM_PATH'):
    load_dotenv()


@pytest.fixture(scope="session")
def test_config():
    return {
        'dicom_path': os.getenv('TEST_DICOM_PATH', ''),
        'dicom_dir': os.getenv('TEST_DICOM_DIR', ''),
    }


@pytest.fixture
def temp_dir():
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def sample_dicom_files(temp_dir) -> List[str]:
    files = []
    for i in range(3):
        file_path = os.path.join(temp_dir, f"sample_{i}.dcm")
        Path(file_path).touch()
        files.append(file_path)
    return files


@pytest.fixture
def sample_invalid_files(temp_dir) -> List[str]:
    files = []
    for name in ["invalid.txt", "image.png", "document.pdf"]:
        file_path = os.path.join(temp_dir, name)
        Path(file_path).touch()
        files.append(file_path)
    return files


@pytest.fixture
def sample_study(sample_dicom_files) -> Study:
    return Study(
        name="TEST-001",
        description="Тестовое исследование",
        files=sample_dicom_files
    )


@pytest.fixture
def sample_studies_list(sample_dicom_files) -> List[Dict]:
    return [
        {
            "name": "STUDY-001",
            "description": "Первый пациент",
            "files": sample_dicom_files
        },
        {
            "name": "STUDY-002",
            "description": "Второй пациент",
            "files": sample_dicom_files
        }
    ]


@pytest.fixture
def mock_inference_result():
    return {
        "studies": [
            {
                "study": "TEST-001",
                "description": "Тестовое исследование",
                "left": {
                    "mean": 10.5,
                    "n_files": 3,
                    "per_model": [
                        {"model": "fold00.pt", "score": 10.2},
                        {"model": "fold01.pt", "score": 10.8}
                    ],
                    "files": [
                        {"path": "/test/left1.dcm", "artery_prob": 0.05},
                        {"path": "/test/left2.dcm", "artery_prob": 0.03}
                    ]
                },
                "right": {
                    "mean": 5.2,
                    "n_files": 2,
                    "per_model": [
                        {"model": "fold00.pt", "score": 5.0},
                        {"model": "fold01.pt", "score": 5.4}
                    ],
                    "files": [
                        {"path": "/test/right1.dcm", "artery_prob": 0.95},
                        {"path": "/test/right2.dcm", "artery_prob": 0.97}
                    ]
                },
                "other": [
                    {"path": "/test/other1.dcm", "artery_prob": 0.5},
                    {"path": "/test/other2.dcm", "artery_prob": 0.3}
                ],
                "total": {
                    "mean": 15.7,
                    "High-risk (≥22.0)": False
                }
            }
        ]
    }


@pytest.fixture
def mock_db_manager():
    mock = MagicMock()
    mock.check_connection.return_value = True
    mock.create_study.return_value = Mock(id=1)
    mock.add_dicom_file.return_value = Mock(id=1)
    mock.save_inference_result.return_value = Mock(id=1)
    return mock


class MockFile:
    def __init__(self, name):
        self.name = name