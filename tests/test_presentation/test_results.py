"""Тесты HTML форматирования результатов: пустые, с ошибками, с риском, с файлами."""

import pytest
from presentation.results import format_results_html


class TestResultsFormatting:

    def test_empty_result(self):
        html = format_results_html({})
        assert "Результаты появятся после запуска анализа" in html

    def test_error_result(self):
        result = {"error": "Тестовая ошибка"}
        html = format_results_html(result)
        assert "Ошибка" in html
        assert "Тестовая ошибка" in html

    def test_single_study_result(self):
        result = {
            "studies": [{
                "study": "TEST-001",
                "description": "Тестовое исследование",
                "left": {"mean": 10.5, "n_files": 3, "per_model": [], "files": []},
                "right": {"mean": 5.2, "n_files": 2, "per_model": [], "files": []},
                "other": [],
                "total": {"mean": 15.7, "High-risk (≥22.0)": False}
            }]
        }
        html = format_results_html(result)
        assert "TEST-001" in html
        assert "Левая артерия" in html
        assert "Правая артерия" in html
        assert "Общий SYNTAX Score" in html
        assert "Низкий риск" in html

    def test_multiple_studies_result(self):
        result = {
            "studies": [
                {
                    "study": "TEST-001",
                    "description": "",
                    "left": {"mean": 10.5, "n_files": 3, "per_model": [], "files": []},
                    "right": {"mean": 5.2, "n_files": 2, "per_model": [], "files": []},
                    "other": [],
                    "total": {"mean": 15.7, "High-risk (≥22.0)": False}
                },
                {
                    "study": "TEST-002",
                    "description": "",
                    "left": {"mean": 18.0, "n_files": 4, "per_model": [], "files": []},
                    "right": {"mean": 8.0, "n_files": 3, "per_model": [], "files": []},
                    "other": [],
                    "total": {"mean": 26.0, "High-risk (≥22.0)": True}
                }
            ]
        }
        html = format_results_html(result)
        assert "TEST-001" in html
        assert "TEST-002" in html
        assert "Низкий риск" in html
        assert "Высокий риск" in html

    def test_high_risk_result(self):
        result = {
            "studies": [{
                "study": "HIGH-RISK",
                "description": "",
                "left": {"mean": 20.0, "n_files": 3, "per_model": [], "files": []},
                "right": {"mean": 15.0, "n_files": 2, "per_model": [], "files": []},
                "other": [],
                "total": {"mean": 35.0, "High-risk (≥22.0)": True}
            }]
        }
        html = format_results_html(result)
        assert "Высокий риск" in html
        assert "Рекомендовано вмешательство" in html

    def test_result_with_other_files(self, mock_inference_result):
        html = format_results_html(mock_inference_result)
        assert "Нераспознанные файлы" in html
        assert "В серой зоне" in html

    def test_result_with_model_scores(self, mock_inference_result):
        html = format_results_html(mock_inference_result)
        assert "SYNTAX Score по моделям" in html
        assert "Модель 1" in html
        assert "Модель 2" in html