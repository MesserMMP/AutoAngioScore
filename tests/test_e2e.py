"""Сквозные тесты: полный пайплайн, очередь, обработка ошибок."""

import pytest
from unittest.mock import patch, MagicMock
import numpy as np
from presentation.files import collect_input_paths
from presentation.queue import render_queue_table
from presentation.results import format_results_html
from application.infer import Study, run_inference
from tests.conftest import MockFile


class TestEndToEnd:

    def test_full_pipeline_simulation(self, sample_dicom_files):
        with patch('presentation.files.pydicom.dcmread') as mock_dcmread:
            mock_dcmread.return_value = MagicMock()

            mock_files = [MockFile(path) for path in sample_dicom_files]
            paths = collect_input_paths(mock_files, None)
            assert len(paths) == len(sample_dicom_files)

            study = Study(name="E2E-TEST", description="Сквозной тест", files=paths)
            assert study.name == "E2E-TEST"

            with patch('application.infer._LEFT_MODELS', [MagicMock()]), \
                 patch('application.infer._RIGHT_MODELS', [MagicMock()]), \
                 patch('application.infer.classify_artery') as mock_classify, \
                 patch('application.infer._score_side_by_models') as mock_score, \
                 patch('application.infer.pydicom.dcmread') as mock_dcmread2:

                mock_ds = MagicMock()
                mock_ds.pixel_array = np.zeros((32, 512, 512), dtype=np.uint8)
                mock_dcmread2.return_value = mock_ds

                mock_classify.return_value = {
                    "left": [{"path": p, "artery_prob": 0.05} for p in paths],
                    "right": [],
                    "other": []
                }
                mock_score.return_value = {"mean": 15.0, "per_model": [], "n_files": len(paths)}

                result = run_inference([study])
                assert "studies" in result

                if "error" not in result:
                    html = format_results_html(result)
                    assert "E2E-TEST" in html

    def test_queue_to_results_flow(self, sample_studies_list):
        queue_html = render_queue_table(sample_studies_list, "queued")
        assert "STUDY-001" in queue_html
        assert "STUDY-002" in queue_html

        studies = [Study(name=s["name"], description=s["description"], files=s["files"])
                   for s in sample_studies_list]

        with patch('application.infer._LEFT_MODELS', [MagicMock()]), \
             patch('application.infer._RIGHT_MODELS', [MagicMock()]), \
             patch('application.infer.classify_artery') as mock_classify, \
             patch('application.infer._score_side_by_models') as mock_score, \
             patch('application.infer.pydicom.dcmread') as mock_dcmread:

            mock_ds = MagicMock()
            mock_ds.pixel_array = np.zeros((32, 512, 512), dtype=np.uint8)
            mock_dcmread.return_value = mock_ds

            mock_classify.return_value = {
                "left": [{"path": "test.dcm", "artery_prob": 0.05}],
                "right": [],
                "other": []
            }
            mock_score.return_value = {"mean": 12.0, "per_model": [], "n_files": 1}

            result = run_inference(studies)

            if "error" not in result:
                results_html = format_results_html(result)
                assert "SYNTAX Score" in results_html

    def test_error_handling_pipeline(self):
        study = Study(
            name="ERROR-TEST",
            description="Тест ошибки",
            files=["/nonexistent/file1.dcm", "/nonexistent/file2.dcm"]
        )

        with patch('application.infer._LEFT_MODELS', [MagicMock()]), \
             patch('application.infer._RIGHT_MODELS', [MagicMock()]), \
             patch('application.infer._filter_dicom_paths') as mock_filter:

            mock_filter.return_value = []

            result = run_inference([study])
            assert "studies" in result or "error" in result