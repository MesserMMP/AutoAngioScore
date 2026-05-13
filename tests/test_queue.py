"""Тесты очереди исследований.

Проверяет:
- Генерацию статусных бейджей (Очередь/Выполняется/Завершено/Ошибка)
- Отображение таблицы очереди с исследованиями
- Пустую очередь и очередь с данными
"""
import pytest
from src.web.queue import status_badge_html, render_queue_table


class TestStatusBadge:
    
    def test_status_queued(self):
        badge = status_badge_html("queued")
        assert "В очереди" in badge
        assert "status-queued" in badge
    
    def test_status_running(self):
        badge = status_badge_html("running")
        assert "Выполняется" in badge
        assert "status-running" in badge
    
    def test_status_running_with_animation(self):
        badge = status_badge_html("running", with_animation=True)
        assert "pulse" in badge
    
    def test_status_done(self):
        badge = status_badge_html("done")
        assert "Завершено" in badge
        assert "status-done" in badge
    
    def test_status_error(self):
        badge = status_badge_html("error")
        assert "Ошибка" in badge
        assert "status-error" in badge
    
    def test_status_unknown(self):
        badge = status_badge_html("unknown")
        assert "В очереди" in badge


class TestRenderQueueTable:
    
    def test_empty_queue(self):
        html = render_queue_table([], "queued")
        assert "Очередь пуста" in html
    
    def test_queue_with_studies(self, sample_studies_list):
        html = render_queue_table(sample_studies_list, "queued")
        assert "STUDY-001" in html
        assert "STUDY-002" in html
        assert "Первый пациент" in html
        assert "Второй пациент" in html
    
    def test_queue_running_status(self, sample_studies_list):
        html = render_queue_table(sample_studies_list, "running")
        assert "Выполняется" in html
    
    def test_queue_done_status(self, sample_studies_list):
        html = render_queue_table(sample_studies_list, "done")
        assert "Завершено" in html