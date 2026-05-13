"""Тесты создания JSON отчётов: пустых, с данными, с ошибками."""

import os
import json
import pytest
from presentation.report import build_report_file


class TestReportBuilding:

    def test_build_report_empty(self):
        result = {}
        file_path = build_report_file(result)
        assert os.path.exists(file_path)
        with open(file_path, 'r') as f:
            data = json.load(f)
        assert data == result
        os.unlink(file_path)

    def test_build_report_with_data(self):
        result = {
            "studies": [
                {
                    "study": "TEST-001",
                    "total": {"mean": 15.7}
                }
            ]
        }
        file_path = build_report_file(result)
        assert os.path.exists(file_path)
        assert file_path.endswith('.json')
        with open(file_path, 'r') as f:
            data = json.load(f)
        assert data["studies"][0]["study"] == "TEST-001"
        os.unlink(file_path)

    def test_build_report_filename_format(self):
        result = {}
        file_path = build_report_file(result)
        filename = os.path.basename(file_path)
        assert filename.startswith("autoangioscore_report_")
        assert filename.endswith(".json")
        os.unlink(file_path)

    def test_build_report_with_error(self):
        result = {"error": "Test error message"}
        file_path = build_report_file(result)
        assert os.path.exists(file_path)
        with open(file_path, 'r') as f:
            data = json.load(f)
        assert "error" in data
        assert data["error"] == "Test error message"
        os.unlink(file_path)