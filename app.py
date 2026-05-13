import os
import base64
import json
import tempfile
from datetime import datetime
from dataclasses import asdict
from typing import List, Dict, Any
from pathlib import Path

import gradio as gr
import pydicom

from src.syntax_pred.config import CFG
from src.syntax_pred.infer import Study, run_inference
from src.database.db_manager import get_db_manager
from src.syntax_pred.infer import extract_dicom_metadata
import time
from sqlalchemy import text


def wait_for_database(max_retries=30, delay=2):
    """Ожидание готовности PostgreSQL"""
    print("\n" + "="*50)
    print("🔍 Проверка подключения к PostgreSQL...")
    print("="*50)
    
    for attempt in range(max_retries):
        try:
            db_manager = get_db_manager()
            with db_manager.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                print("✅ PostgreSQL готов к работе!")
                return True
        except Exception as e:
            print(f"⏳ Ожидание PostgreSQL... (попытка {attempt + 1}/{max_retries})")
            time.sleep(delay)
    
    print("⚠️ PostgreSQL не доступен, продолжаем без сохранения в БД")
    return False


# ==================== КОНФИГУРАЦИЯ ДИЗАЙНА ====================
APPLE_STYLE_CSS = """
/* Сбалансированная современная цветовая гамма */
:root {
    --bg-primary: #4f46e5;
    --bg-secondary: #7c3aed;
    --bg-gradient: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #a855f7 100%);
    --bg-surface: linear-gradient(135deg, rgba(255,255,255,0.97) 0%, rgba(255,255,255,0.94) 100%);
    
    --accent-cyan: #06b6d4;
    --accent-teal: #3b82f6;
    --accent-purple: #8b5cf6;
    --accent-pink: #d946ef;
    --accent-orange: #f97316;
    --accent-green: #10b981;
    --accent-red: #ef4444;
    --accent-yellow: #eab308;
    
    --accent-cyan-light: rgba(6, 182, 212, 0.08);
    --accent-teal-light: rgba(59, 130, 246, 0.08);
    --accent-purple-light: rgba(139, 92, 246, 0.08);
    --accent-pink-light: rgba(217, 70, 239, 0.08);
    --accent-green-light: rgba(16, 185, 129, 0.08);
    --accent-red-light: rgba(239, 68, 68, 0.08);
    --accent-orange-light: rgba(249, 115, 22, 0.08);
    
    --text-primary: #1e293b;
    --text-secondary: #64748b;
    --text-light: #94a3b8;
    --text-white: #ffffff;
    
    --border-color: rgba(255, 255, 255, 0.2);
    --border-dark: rgba(0, 0, 0, 0.06);
    --shadow-sm: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    --shadow-md: 0 10px 15px -3px rgba(0, 0, 0, 0.08);
    --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.1);
    --shadow-glow: 0 0 0 3px rgba(6, 182, 212, 0.2);
    --shadow-glow-purple: 0 0 0 3px rgba(139, 92, 246, 0.2);
}

* {
    font-family: -apple-system, "SF Pro Text", "SF Pro Display", "Inter", "Helvetica Neue", system-ui, sans-serif;
}

body, .gradio-container {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 50%, #a855f7 100%) !important;
    position: relative;
}

body::before {
    content: '';
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: radial-gradient(circle at 20% 50%, rgba(255,255,255,0.08) 0%, transparent 70%);
    pointer-events: none;
    z-index: 0;
}

.gradio-container {
    position: relative;
    z-index: 1;
}

.gr-box, .gr-form, .panel, .tabs, .tab-nav, .accordion {
    background: transparent !important;
    border: none !important;
}

.apple-container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 2rem 1.5rem;
}

.apple-header {
    text-align: center;
    margin-bottom: 2rem;
    position: relative;
    padding: 1rem 0;
}

.apple-title {
    font-size: 3.2rem;
    font-weight: 800;
    background: linear-gradient(135deg, #ffffff 0%, #e2e8f0 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    letter-spacing: -0.02em;
    margin: 0;
    text-shadow: 0 2px 10px rgba(0,0,0,0.05);
}

.apple-subtitle {
    font-size: 1.1rem;
    color: rgba(255, 255, 255, 0.85);
    margin-top: 0.5rem;
    font-weight: 400;
}

.apple-card {
    background: rgba(255, 255, 255, 0.96);
    backdrop-filter: blur(20px);
    border-radius: 24px;
    border: 1px solid rgba(255, 255, 255, 0.3);
    box-shadow: var(--shadow-md);
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    overflow: hidden;
}

.apple-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow-lg);
    background: rgba(255, 255, 255, 0.98);
}

.apple-card-header {
    padding: 1.25rem 1.5rem;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
    background: linear-gradient(135deg, rgba(255,255,255,0.4) 0%, rgba(255,255,255,0.2) 100%);
}

.apple-card-title {
    font-size: 1.25rem;
    font-weight: 700;
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
    margin: 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.apple-card-content {
    padding: 1.5rem;
}

.add-study-card {
    background: linear-gradient(135deg, rgba(255,255,255,0.98) 0%, rgba(255,255,255,0.96) 100%);
    border: 1px solid rgba(255,255,255,0.4);
    position: relative;
    overflow: hidden;
}

.apple-button {
    background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
    color: white;
    border: none;
    border-radius: 980px;
    padding: 0.75rem 1.5rem;
    font-size: 0.9375rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: var(--shadow-sm);
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    position: relative;
    overflow: hidden;
}

.apple-button::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
    transition: left 0.5s;
}

.apple-button:hover::before {
    left: 100%;
}

.apple-button:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
    background: linear-gradient(135deg, #0891b2 0%, #2563eb 100%);
}

.apple-button-add {
    background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%);
    color: white;
    border: none;
    border-radius: 980px;
    padding: 0.75rem 1.5rem;
    font-size: 0.9375rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: var(--shadow-sm);
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    position: relative;
    overflow: hidden;
}

.apple-button-add::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
    transition: left 0.5s;
}

.apple-button-add:hover::before {
    left: 100%;
}

.apple-button-add:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
    background: linear-gradient(135deg, #7c3aed 0%, #9333ea 100%);
}

.apple-button-clear {
    background: linear-gradient(135deg, #f97316 0%, #fbbf24 100%);
    color: white;
    border: none;
    border-radius: 980px;
    padding: 0.75rem 1.5rem;
    font-size: 0.9375rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.3s ease;
    box-shadow: var(--shadow-sm);
    display: inline-flex;
    align-items: center;
    gap: 0.5rem;
    position: relative;
    overflow: hidden;
}

.apple-button-clear::before {
    content: '';
    position: absolute;
    top: 0;
    left: -100%;
    width: 100%;
    height: 100%;
    background: linear-gradient(90deg, transparent, rgba(255,255,255,0.15), transparent);
    transition: left 0.5s;
}

.apple-button-clear:hover::before {
    left: 100%;
}

.apple-button-clear:hover {
    transform: translateY(-1px);
    box-shadow: var(--shadow-md);
    background: linear-gradient(135deg, #ea580c 0%, #eab308 100%);
}

.apple-input {
    border: 1.5px solid rgba(0, 0, 0, 0.05) !important;
    border-radius: 14px !important;
    padding: 0.75rem 1rem !important;
    font-size: 0.9375rem !important;
    background: rgba(255, 255, 255, 0.95) !important;
    transition: all 0.3s ease !important;
}

.apple-input:focus {
    outline: none !important;
    border-color: #06b6d4 !important;
    box-shadow: var(--shadow-glow) !important;
    background: white !important;
}

.apple-table {
    border-radius: 16px;
    overflow: hidden;
    border: none;
}

.apple-table table {
    background: rgba(255, 255, 255, 0.95) !important;
    border-collapse: collapse !important;
    width: 100%;
}

.apple-table th {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%) !important;
    color: white !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    padding: 12px 16px !important;
    border-bottom: none !important;
    border-top: none !important;
    border-left: none !important;
    border-right: none !important;
}

.apple-table td {
    background: rgba(255, 255, 255, 0.98) !important;
    color: var(--text-primary) !important;
    padding: 12px 16px !important;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05) !important;
    border-top: none !important;
    border-left: none !important;
    border-right: none !important;
}

.apple-table tr:last-child td {
    border-bottom: none !important;
}

.apple-table tr:hover td {
    background: rgba(139, 92, 246, 0.04) !important;
}

.queue-table {
    width: 100%;
    border-collapse: separate;
    border-spacing: 0;
    overflow: hidden;
    border-radius: 16px;
    box-shadow: var(--shadow-sm);
}

.queue-table thead th {
    background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
    color: #ffffff;
    font-size: 0.875rem;
    font-weight: 700;
    text-align: left;
    padding: 0.9rem 1rem;
    border-bottom: none;
}

.queue-table tbody td {
    background: rgba(255, 255, 255, 0.98);
    color: var(--text-primary);
    padding: 0.9rem 1rem;
    border-bottom: 1px solid rgba(0, 0, 0, 0.05);
    vertical-align: top;
}

.queue-table tbody tr:last-child td {
    border-bottom: none;
}

.queue-table tbody tr:hover td {
    background: rgba(139, 92, 246, 0.04);
}

.queue-empty {
    padding: 1rem;
    text-align: center;
    color: var(--text-secondary);
    font-size: 0.875rem;
}

.status-badge {
    display: inline-flex;
    align-items: center;
    gap: 0.375rem;
    padding: 0.25rem 0.75rem;
    border-radius: 20px;
    font-size: 0.8125rem;
    font-weight: 600;
    white-space: nowrap;
}

.status-running {
    background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
    color: white;
    box-shadow: var(--shadow-sm);
}

.status-done {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    box-shadow: var(--shadow-sm);
}

.status-error {
    background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%);
    color: white;
    box-shadow: var(--shadow-sm);
}

.status-queued {
    background: linear-gradient(135deg, #64748b 0%, #475569 100%);
    color: white;
    box-shadow: var(--shadow-sm);
}

@keyframes pulse {
    0%, 100% { 
        opacity: 1;
        transform: scale(1);
    }
    50% { 
        opacity: 0.85;
        transform: scale(1.02);
    }
}

.pulse {
    animation: pulse 1.5s ease-in-out infinite;
}

::-webkit-scrollbar {
    width: 8px;
    height: 8px;
}

::-webkit-scrollbar-track {
    background: rgba(255, 255, 255, 0.15);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb {
    background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
    border-radius: 4px;
}

::-webkit-scrollbar-thumb:hover {
    background: linear-gradient(135deg, #0891b2 0%, #2563eb 100%);
}

.upload-grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 1rem;
}

.instruction-box {
    background: linear-gradient(135deg, rgba(139, 92, 246, 0.06) 0%, rgba(6, 182, 212, 0.06) 100%);
    border-radius: 16px;
    padding: 1rem;
    margin-top: 1rem;
    border: 1px solid rgba(139, 92, 246, 0.15);
    backdrop-filter: blur(10px);
}

.instruction-title {
    font-size: 0.875rem;
    font-weight: 700;
    background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin-bottom: 0.5rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.instruction-list {
    list-style: none;
    padding: 0;
    margin: 0;
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 0.5rem;
}

.instruction-list li {
    font-size: 0.8125rem;
    color: var(--text-secondary);
    display: flex;
    align-items: center;
    gap: 0.5rem;
    font-weight: 500;
}

@media (max-width: 768px) {
    .upload-grid {
        grid-template-columns: 1fr;
        gap: 1rem;
    }
    
    .instruction-list {
        grid-template-columns: 1fr;
    }
    
    .apple-title {
        font-size: 2rem;
    }
}
"""

# Логотип (base64)
DEFAULT_LOGO = "assets/logo.png"
LOGO_PATH = os.environ.get("LOGO_PATH", DEFAULT_LOGO)


def _logo_html() -> str:
    """Генерация HTML для логотипа"""
    path = LOGO_PATH
    if not path or not os.path.exists(path):
        return ""
    try:
        with open(path, "rb") as f:
            data = base64.b64encode(f.read()).decode("ascii")
        ext = os.path.splitext(path)[1].lower()
        mime = "image/png" if ext in {".png", ""} else "image/jpeg"
        return f'<img src="data:{mime};base64,{data}" alt="Логотип" style="height: 36px; width: auto; border-radius: 10px; filter: drop-shadow(0 2px 6px rgba(0,0,0,0.08));" />'
    except Exception:
        return ""


def _is_dicom_path(path: str) -> bool:
    """Проверка на DICOM файл"""
    if not os.path.exists(path):
        return False
    ext = os.path.splitext(path)[1].lower()
    if ext not in {".dcm", ""}:
        return False
    try:
        pydicom.dcmread(path, stop_before_pixels=True)
        return True
    except Exception:
        return False


def _files_to_paths(files) -> List[str]:
    """Конвертация файлов в пути"""
    if not files:
        return []
    raw_paths = [f.name for f in files if hasattr(f, "name") and os.path.exists(f.name)]
    return [p for p in raw_paths if _is_dicom_path(p)]


def _collect_input_paths(files_all, folder_files) -> List[str]:
    """Сбор всех путей из загрузок"""
    combined = _files_to_paths(files_all) + _files_to_paths(folder_files)
    return list(dict.fromkeys(combined))


def _build_report_file(result: Dict[str, Any]) -> str:
    """Создание отчета в JSON"""
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    with tempfile.NamedTemporaryFile(
        mode="w",
        prefix=f"autoangioscore_report_{ts}_",
        suffix=".json",
        encoding="utf-8",
        delete=False,
    ) as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
        return f.name


def _status_badge_html(state: str, with_animation: bool = False) -> str:
    """Генерация HTML для статус бейджа"""
    state = state.lower()
    
    status_config = {
        "running": {"class": "status-running", "icon": "⏱️", "text": "Выполняется"},
        "done": {"class": "status-done", "icon": "✅", "text": "Завершено"},
        "error": {"class": "status-error", "icon": "❌", "text": "Ошибка"},
        "queued": {"class": "status-queued", "icon": "⏳", "text": "В очереди"}
    }
    
    config = status_config.get(state, status_config["queued"])
    animation_class = " pulse" if with_animation and state == "running" else ""
    
    return f'<span class="status-badge {config["class"]}{animation_class}">{config["icon"]} {config["text"]}</span>'


def _update_status_table(studies, status: str) -> str:
    """Обновление таблицы со статусами в HTML."""
    studies = studies or []

    if not studies:
        return '''
        <div class="apple-card" style="padding: 1rem; text-align: center;">
            <div style="color: var(--text-secondary); font-size: 0.875rem;">
                Очередь пуста
            </div>
        </div>
        '''

    badge = _status_badge_html(status, with_animation=(status == "running"))
    rows_html = []
    for idx, s in enumerate(studies, 1):
        rows_html.append(f'''
            <tr>
                <td>{idx}</td>
                <td>{s.get("name", "-")}</td>
                <td>{s.get("description", "-") or "-"}</td>
                <td style="text-align: center;">{len(s.get("files", []))}</td>
                <td style="text-align: center;">{badge}</td>
            </tr>
        ''')

    return f'''
    <div style="overflow-x: auto;">
        <table class="queue-table">
            <thead>
                <tr>
                    <th>#</th>
                    <th>Исследование</th>
                    <th>Описание</th>
                    <th>Файлов</th>
                    <th>Статус</th>
                </tr>
            </thead>
            <tbody>
                {''.join(rows_html)}
            </tbody>
        </table>
    </div>
    '''


def _format_results_html(result: Dict[str, Any]) -> str:
    """Форматирование результатов в красивом HTML с детальной информацией (одна кнопка на исследование)"""
    if not result:
        return '''
        <div class="apple-card" style="padding: 2rem; text-align: center;">
            <div style="color: var(--text-secondary);">
                📊 Результаты появятся после запуска анализа
            </div>
        </div>
        '''
    
    if "error" in result:
        return f'''
        <div class="apple-card" style="padding: 1.5rem; background: linear-gradient(135deg, rgba(239,68,68,0.10) 0%, rgba(220,38,38,0.10) 100%);">
            <div style="color: var(--accent-red); display: flex; align-items: center; gap: 0.75rem;">
                <span style="font-size: 1.5rem;">⚠️</span>
                <div>
                    <strong>Ошибка</strong>
                    <div style="margin-top: 0.25rem;">{result.get("error", "Неизвестная ошибка")}</div>
                </div>
            </div>
        </div>
        '''
    
    studies = result.get("studies", []) or []
    if not studies:
        return '''
        <div class="apple-card" style="padding: 2rem; text-align: center;">
            <div style="color: var(--text-secondary);">
                📋 Нет исследований для отображения
            </div>
        </div>
        '''
    
    # Добавляем стили для аккордеона и кнопки (без JavaScript)
    accordion_styles = """
    <style>
    .detail-accordion {
        margin-top: 1rem;
        border-radius: 12px;
        overflow: hidden;
    }
    .detail-accordion summary {
        cursor: pointer;
        list-style: none;
        display: flex;
        align-items: center;
        justify-content: center;
        padding: 0;
    }
    .detail-accordion summary::-webkit-details-marker {
        display: none;
    }
    .detail-button {
        background: linear-gradient(135deg, #4f46e5 0%, #7c3aed 100%);
        color: white;
        border: none;
        border-radius: 980px;
        padding: 0.6rem 1.5rem;
        font-size: 0.875rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
        display: inline-flex;
        align-items: center;
        gap: 0.5rem;
        margin: 0 auto;
    }
    .detail-button:hover {
        transform: translateY(-1px);
        box-shadow: var(--shadow-md);
        background: linear-gradient(135deg, #5b52e8 0%, #8b4ced 100%);
    }
    .detail-accordion[open] .detail-button {
        background: linear-gradient(135deg, #f97316 0%, #fbbf24 100%);
    }
    .detail-accordion[open] .detail-button:hover {
        background: linear-gradient(135deg, #ea580c 0%, #eab308 100%);
    }
    /* Меняем текст кнопки через CSS псевдоэлементы */
    .detail-button .toggle-text-open {
        display: inline;
    }
    .detail-button .toggle-text-close {
        display: none;
    }
    .detail-accordion[open] .detail-button .toggle-text-open {
        display: none;
    }
    .detail-accordion[open] .detail-button .toggle-text-close {
        display: inline;
    }
    .detail-button .toggle-icon-open {
        display: inline;
    }
    .detail-button .toggle-icon-close {
        display: none;
    }
    .detail-accordion[open] .detail-button .toggle-icon-open {
        display: none;
    }
    .detail-accordion[open] .detail-button .toggle-icon-close {
        display: inline;
    }
    .files-list {
        margin-top: 8px;
        max-height: 300px;
        overflow-y: auto;
    }
    .file-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 11px;
        padding: 6px 0;
        border-bottom: 1px solid rgba(0,0,0,0.05);
    }
    .file-name {
        color: var(--text-secondary);
        font-size: 11px;
    }
    .file-prob {
        font-weight: 500;
        font-size: 11px;
    }
    .other-file-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 11px;
        padding: 6px 0;
        border-bottom: 1px solid rgba(0,0,0,0.05);
    }
    .other-file-info {
        display: flex;
        flex-direction: column;
        align-items: flex-start;
    }
    .other-file-name {
        color: var(--text-secondary);
        font-size: 11px;
    }
    .other-file-status {
        font-size: 9px;
    }
    .other-file-prob {
        text-align: right;
    }
    .other-file-prob-value {
        font-weight: 600;
        font-size: 11px;
    }
    .other-file-prob-label {
        font-size: 9px;
        color: var(--text-light);
    }
    </style>
    """
    
    cards_html = [accordion_styles]
    
    for idx, s in enumerate(studies):
        study_name = s.get("study", "-")
        description = s.get("description", "")
        unique_id = f"details_{idx}_{study_name.replace(' ', '_').replace('/', '_')}"
        
        left_data = s.get("left", {})
        right_data = s.get("right", {})
        other_data = s.get("other", [])
        total_obj = s.get("total", {})
        
        left_mean = left_data.get("mean", 0.0)
        right_mean = right_data.get("mean", 0.0)
        total_mean = total_obj.get("mean", 0.0)
        
        left_files_count = left_data.get("n_files", 0)
        right_files_count = right_data.get("n_files", 0)
        other_files_count = len(other_data)
        
        left_per_model = left_data.get("per_model", [])
        right_per_model = right_data.get("per_model", [])
        
        risk_key = next((k for k in total_obj.keys() if "High-risk" in str(k)), None)
        is_high_risk = bool(total_obj.get(risk_key, False)) if risk_key else total_mean > 0.5
        
        if is_high_risk:
            badge_bg = "#fee2e2"
            badge_color = "#991b1b"
            badge_text = "⚠️ Высокий риск"
        else:
            badge_bg = "#dcfce7"
            badge_color = "#14532d"
            badge_text = "✅ Низкий риск"
        
        badge_style = f"""
            background: {badge_bg};
            color: {badge_color};
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 700;
            display: inline-flex;
            align-items: center;
            gap: 6px;
            border: 1px solid rgba(0,0,0,0.05);
        """
        
        # Генерация HTML для моделей левой артерии
        left_models_html = ""
        if left_per_model:
            left_models_html = '<div style="margin-top: 8px;">'
            for i, model_info in enumerate(left_per_model, 1):
                model_score = model_info.get("score", 0.0)
                left_models_html += f'''
                    <div class="file-item">
                        <span class="file-name">🎯 Модель {i}</span>
                        <span class="file-prob" style="color: #06b6d4;">{model_score:.3f}</span>
                    </div>
                '''
            left_models_html += '</div>'
        else:
            left_models_html = '<div style="margin-top: 8px; font-size: 11px; color: var(--text-light); text-align: center;">Нет данных моделей</div>'
        
        # Генерация HTML для моделей правой артерии
        right_models_html = ""
        if right_per_model:
            right_models_html = '<div style="margin-top: 8px;">'
            for i, model_info in enumerate(right_per_model, 1):
                model_score = model_info.get("score", 0.0)
                right_models_html += f'''
                    <div class="file-item">
                        <span class="file-name">🎯 Модель {i}</span>
                        <span class="file-prob" style="color: #8b5cf6;">{model_score:.3f}</span>
                    </div>
                '''
            right_models_html += '</div>'
        else:
            right_models_html = '<div style="margin-top: 8px; font-size: 11px; color: var(--text-light); text-align: center;">Нет данных моделей</div>'
        
        # Файлы левой артерии (ВСЕ файлы)
        left_files_with_probs = left_data.get("files", [])
        left_files_html = ""
        if left_files_with_probs:
            left_files_html = '<div class="files-list">'
            for file_info in left_files_with_probs:
                file_path = file_info.get("path", "unknown")
                file_name = os.path.basename(file_path) if file_path else "unknown"
                artery_prob = file_info.get("artery_prob", 0.0)
                left_files_html += f'''
                    <div class="file-item">
                        <span class="file-name">📄 {file_name[:50]}</span>
                        <span class="file-prob" style="color: #06b6d4;">{artery_prob:.3f}</span>
                    </div>
                '''
            left_files_html += '</div>'
        else:
            left_files_html = '<div style="margin-top: 8px; font-size: 11px; color: var(--text-light); text-align: center;">Нет файлов</div>'
        
        # Файлы правой артерии (ВСЕ файлы)
        right_files_with_probs = right_data.get("files", [])
        right_files_html = ""
        if right_files_with_probs:
            right_files_html = '<div class="files-list">'
            for file_info in right_files_with_probs:
                file_path = file_info.get("path", "unknown")
                file_name = os.path.basename(file_path) if file_path else "unknown"
                artery_prob = file_info.get("artery_prob", 0.0)
                right_files_html += f'''
                    <div class="file-item">
                        <span class="file-name">📄 {file_name[:50]}</span>
                        <span class="file-prob" style="color: #8b5cf6;">{artery_prob:.3f}</span>
                    </div>
                '''
            right_files_html += '</div>'
        else:
            right_files_html = '<div style="margin-top: 8px; font-size: 11px; color: var(--text-light); text-align: center;">Нет файлов</div>'
        
        # Нераспознанные файлы (ВСЕ файлы)
        other_files_html = ""
        if other_data:
            other_files_html = '<div class="files-list">'
            for file_info in other_data:
                file_path = file_info.get("path", "unknown")
                file_name = os.path.basename(file_path) if file_path else "unknown"
                artery_prob = file_info.get("artery_prob", 0.0)
                
                left_threshold = 0.10
                right_threshold = 0.90
                
                if artery_prob <= left_threshold:
                    prob_status = "⚠️ Ниже порога левой артерии"
                    prob_color = "#f97316"
                elif artery_prob >= right_threshold:
                    prob_status = "⚠️ Выше порога правой артерии"
                    prob_color = "#f97316"
                else:
                    prob_status = "❓ В серой зоне (неопределён)"
                    prob_color = "#ef4444"
                
                other_files_html += f'''
                    <div class="other-file-item">
                        <div class="other-file-info">
                            <span class="other-file-name">📄 {file_name[:50]}</span>
                            <span class="other-file-status" style="color: {prob_color};">{prob_status}</span>
                        </div>
                        <div class="other-file-prob">
                            <div class="other-file-prob-value" style="color: #f97316;">{artery_prob:.3f}</div>
                            <div class="other-file-prob-label">вероятность</div>
                        </div>
                    </div>
                '''
            other_files_html += '</div>'
        else:
            other_files_html = '<div style="margin-top: 8px; font-size: 11px; color: var(--text-light); text-align: center;">Нераспознанных файлов нет</div>'
        
        card_html = f'''
        <div class="apple-card" style="margin-bottom: 1rem;">
            <div class="apple-card-header">
                <div style="display: flex; align-items: center; justify-content: space-between; flex-wrap: wrap; gap: 10px;">
                    <div style="display: flex; align-items: center; gap: 8px;">
                        <span style="font-size: 1.25rem; font-weight: 700; color: var(--text-primary);">🏥 {study_name}</span>
                    </div>
                    <div style="{badge_style}">
                        {badge_text}
                    </div>
                </div>
                {f'<div style="font-size: 0.875rem; color: var(--text-secondary); margin-top: 0.5rem;">{description}</div>' if description else ''}
            </div>
            <div class="apple-card-content">
                
                <!-- Три основных показателя (всегда видны) -->
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; margin-bottom: 0rem;">
                    
                    <div style="text-align: center; 
                        background: linear-gradient(135deg, rgba(6,182,212,0.10) 0%, rgba(59,130,246,0.10) 100%);
                        border-radius: 16px; 
                        padding: 0.85rem;
                        border: 1px solid rgba(59,130,246,0.15);">
                        <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                            🧬 Левая артерия
                        </div>
                        <div style="font-size: 1.5rem; font-weight: 800; 
                            background: linear-gradient(135deg, #06b6d4 0%, #3b82f6 100%);
                            -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                            {left_mean:.3f}
                        </div>
                        <div style="font-size: 0.7rem; color: var(--text-secondary); margin-top: 0.25rem;">
                            SYNTAX Score
                        </div>
                        <div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 0.25rem;">
                            📁 {left_files_count} файлов
                        </div>
                    </div>

                    <div style="text-align: center; 
                        background: linear-gradient(135deg, rgba(139,92,246,0.10) 0%, rgba(168,85,247,0.10) 100%);
                        border-radius: 16px; 
                        padding: 0.85rem;
                        border: 1px solid rgba(168,85,247,0.15);">
                        <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                            🧬 Правая артерия
                        </div>
                        <div style="font-size: 1.5rem; font-weight: 800; 
                            background: linear-gradient(135deg, #8b5cf6 0%, #a855f7 100%);
                            -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                            {right_mean:.3f}
                        </div>
                        <div style="font-size: 0.7rem; color: var(--text-secondary); margin-top: 0.25rem;">
                            SYNTAX Score
                        </div>
                        <div style="font-size: 0.7rem; color: var(--text-muted); margin-top: 0.25rem;">
                            📁 {right_files_count} файлов
                        </div>
                    </div>

                    <div style="text-align: center; 
                        background: linear-gradient(135deg, rgba(249,115,22,0.10) 0%, rgba(251,191,36,0.10) 100%);
                        border-radius: 16px; 
                        padding: 0.85rem;
                        border: 1px solid rgba(249,115,22,0.20);">
                        <div style="font-size: 0.875rem; color: var(--text-secondary); margin-bottom: 0.5rem;">
                            📊 Общий SYNTAX Score
                        </div>
                        <div style="font-size: 1.75rem; font-weight: 900; 
                            background: linear-gradient(135deg, #f97316 0%, #fbbf24 100%);
                            -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                            {total_mean:.3f}
                        </div>
                        <div style="font-size: 0.7rem; color: var(--text-secondary); margin-top: 0.25rem;">
                            {'⚠️ Рекомендовано вмешательство' if is_high_risk else '✅ Плановое наблюдение'}
                        </div>
                    </div>

                </div>
                
                <!-- Кнопка для раскрытия детальной информации (без JavaScript, через CSS) -->
                <details id="{unique_id}" class="detail-accordion">
                    <summary>
                        <div class="detail-button">
                            <span class="toggle-icon-open">▼</span>
                            <span class="toggle-icon-close">▲</span>
                            <span class="toggle-text-open">Показать детальную информацию</span>
                            <span class="toggle-text-close">Скрыть детальную информацию</span>
                        </div>
                    </summary>
                    
                    <!-- Детальная информация (появляется после клика) -->
                    <div style="margin-top: 1.5rem;">
                        
                        <!-- Оценка по моделям -->
                        <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 1rem; margin-bottom: 1rem;">
                            
                            <div style="background: rgba(6,182,212,0.04); border-radius: 12px; padding: 0.75rem; border: 1px solid rgba(6,182,212,0.1);">
                                <div style="font-size: 0.8125rem; font-weight: 700; color: #06b6d4; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                                    <span>🎯</span> SYNTAX Score по моделям (левая артерия)
                                </div>
                                {left_models_html}
                            </div>
                            
                            <div style="background: rgba(139,92,246,0.04); border-radius: 12px; padding: 0.75rem; border: 1px solid rgba(139,92,246,0.1);">
                                <div style="font-size: 0.8125rem; font-weight: 700; color: #8b5cf6; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                                    <span>🎯</span> SYNTAX Score по моделям (правая артерия)
                                </div>
                                {right_models_html}
                            </div>
                            
                        </div>
                        
                        <!-- Файлы левой артерии (ВСЕ) -->
                        <div style="background: rgba(6,182,212,0.03); border-radius: 12px; padding: 0.75rem; margin-bottom: 0.75rem; border: 1px solid rgba(6,182,212,0.1);">
                            <div style="font-size: 0.75rem; font-weight: 700; color: #06b6d4; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                                <span>📂</span> Файлы левой артерии (вероятность ≤ 0.10)
                                <span style="background: #06b6d4; color: white; padding: 0 6px; border-radius: 12px; font-size: 9px;">{left_files_count}</span>
                            </div>
                            {left_files_html}
                        </div>
                        
                        <!-- Файлы правой артерии (ВСЕ) -->
                        <div style="background: rgba(139,92,246,0.03); border-radius: 12px; padding: 0.75rem; margin-bottom: 0.75rem; border: 1px solid rgba(139,92,246,0.1);">
                            <div style="font-size: 0.75rem; font-weight: 700; color: #8b5cf6; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                                <span>📂</span> Файлы правой артерии (вероятность ≥ 0.90)
                                <span style="background: #8b5cf6; color: white; padding: 0 6px; border-radius: 12px; font-size: 9px;">{right_files_count}</span>
                            </div>
                            {right_files_html}
                        </div>
                        
                        <!-- Нераспознанные файлы (ВСЕ) -->
                        <div style="background: rgba(249,115,22,0.03); border-radius: 12px; padding: 0.75rem; border: 1px solid rgba(249,115,22,0.1);">
                            <div style="font-size: 0.75rem; font-weight: 700; color: #f97316; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                                <span>❓</span> Нераспознанные файлы (0.10 < вероятность < 0.90)
                                <span style="background: #f97316; color: white; padding: 0 6px; border-radius: 12px; font-size: 9px;">{other_files_count}</span>
                            </div>
                            {other_files_html}
                            <div style="font-size: 0.65rem; color: var(--text-light); margin-top: 0.5rem; padding-top: 0.25rem; border-top: 1px solid rgba(0,0,0,0.05);">
                                💡 Вероятность классификации артерии: ≤0.10 → левая, ≥0.90 → правая
                            </div>
                        </div>
                        
                    </div>
                </details>
                
                <!-- Дополнительная статистика (всегда видна) -->
                <div style="margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid rgba(0,0,0,0.05); display: flex; justify-content: space-between; font-size: 0.65rem; color: var(--text-light);">
                    <span>🎯 Порог высокого риска SYNTAX: ≥22.0</span>
                    <span>🧠 Ансамбль моделей: {len(left_per_model)} левых / {len(right_per_model)} правых</span>
                </div>
            </div>
        </div>
        '''
        cards_html.append(card_html)
    
    return "".join(cards_html)

# ==================== ОСНОВНОЙ UI ====================

def create_ui():
    """Создание интерфейса в стиле Apple"""
    
    with gr.Blocks(title="AutoAngioScore") as demo:
        
        # Главный контейнер
        with gr.Column(elem_classes="apple-container"):
            
            # Хедер
            with gr.Row(elem_classes="apple-header"):
                with gr.Column(scale=1, min_width=0):
                    logo_html = _logo_html()
                    if logo_html:
                        gr.HTML(f'<div style="margin-bottom: 1rem;">{logo_html}</div>')
                    
                    gr.HTML('''
                        <h1 class="apple-title">AutoAngioScore</h1>
                        <p class="apple-subtitle">Автоматическая оценка степени коронарного поражения по видеозаписям ангиографии</p>
                    ''')
            
            # ==================== БЛОК ДОБАВЛЕНИЯ ИССЛЕДОВАНИЯ ====================
            with gr.Group(elem_classes="apple-card add-study-card"):
                with gr.Column(elem_classes="apple-card-header"):
                    gr.HTML('<h3 class="apple-card-title">✨ Добавление нового исследования</h3>')
                
                with gr.Column(elem_classes="apple-card-content"):
                    # Информация об исследовании
                    with gr.Row():
                        study_name = gr.Textbox(
                            label="Идентификатор исследования",
                            placeholder="Например: INV-2024-001",
                            elem_classes="apple-input",
                            scale=1
                        )
                        study_desc = gr.Textbox(
                            label="Описание (необязательно)",
                            placeholder="Клинические данные, особенности...",
                            elem_classes="apple-input",
                            scale=1
                        )
                    
                    # Загрузка DICOM - две колонки
                    gr.HTML('<div class="upload-grid">')
                    
                    with gr.Column(elem_classes="apple-card", variant="panel"):
                        with gr.Column(elem_classes="apple-card-header"):
                            gr.HTML('<h3 class="apple-card-title" style="font-size: 1rem;">📄 Отдельные файлы</h3>')
                        
                        with gr.Column(elem_classes="apple-card-content"):
                            files_all = gr.File(
                                label="Выберите DICOM файлы",
                                file_count="multiple",
                                elem_classes="apple-input"
                            )
                            gr.HTML('''
                                <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.5rem;">
                                    ✓ Поддерживаются файлы .dcm
                                </div>
                            ''')
                    
                    with gr.Column(elem_classes="apple-card", variant="panel"):
                        with gr.Column(elem_classes="apple-card-header"):
                            gr.HTML('<h3 class="apple-card-title" style="font-size: 1rem;">📁 Папка с исследованием</h3>')
                        
                        with gr.Column(elem_classes="apple-card-content"):
                            files_folder = gr.File(
                                label="Выберите папку",
                                file_count="directory",
                                elem_classes="apple-input"
                            )
                            gr.HTML('''
                                <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.5rem;">
                                    ✓ Выберите папку, содержащую DICOM файлы
                                </div>
                            ''')
                    
                    gr.HTML('</div>')
                    
                    # Кнопки управления добавлением
                    with gr.Row():
                        btn_add = gr.Button(
                            "✨ Добавить в очередь",
                            elem_classes="apple-button-add",
                            scale=1
                        )
                        btn_clear = gr.Button(
                            "🗑️ Очистить форму",
                            elem_classes="apple-button-clear",
                            scale=1
                        )
                    
                    # Краткая инструкция
                    gr.HTML('''
                        <div class="instruction-box">
                            <div class="instruction-title">
                                <span>🎯</span> Быстрый старт
                            </div>
                            <ul class="instruction-list">
                                <li>📝 1. Укажите ID исследования</li>
                                <li>📂 2. Загрузите DICOM файлы</li>
                                <li>➕ 3. Добавьте в очередь</li>
                                <li>🚀 4. Запустите анализ</li>
                            </ul>
                        </div>
                    ''')
            
            # ==================== ОЧЕРЕДЬ ИССЛЕДОВАНИЙ ====================
            with gr.Group(elem_classes="apple-card"):
                with gr.Column(elem_classes="apple-card-header"):
                    gr.HTML('<h3 class="apple-card-title">📋 Очередь исследований</h3>')
                
                with gr.Column(elem_classes="apple-card-content"):
                    queue_table = gr.HTML(
                        value=_update_status_table([], "Queued"),
                        elem_classes="apple-table"
                    )
                    
                    gr.HTML('''
                        <div style="font-size: 0.8125rem; color: var(--text-secondary); margin-top: 0.75rem; text-align: center;">
                            💡 Добавьте исследования в очередь для пакетного анализа
                        </div>
                    ''')
            
            # ==================== ЗАПУСК АНАЛИЗА ====================
            with gr.Row():
                run_btn = gr.Button(
                    "🚀 Запустить анализ очереди",
                    elem_classes="apple-button"
                )
            
            # ==================== РЕЗУЛЬТАТЫ ====================
            with gr.Group(elem_classes="apple-card"):
                with gr.Column(elem_classes="apple-card-header"):
                    gr.HTML('<h3 class="apple-card-title">📊 Результаты анализа</h3>')
                
                with gr.Column(elem_classes="apple-card-content"):
                    out_summary = gr.HTML(label="")
                    out_json = gr.JSON(label="Подробные данные", visible=False)  # Скрытый JSON для логики
                    
                    with gr.Row():
                        out_report = gr.File(
                            label="📥 Скачать отчет JSON",
                            interactive=False,
                            elem_classes="apple-input"
                        )
            
            # Footer
            gr.HTML('''
                <div style="margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid rgba(255,255,255,0.15); text-align: center; font-size: 0.75rem; color: rgba(255,255,255,0.7);">
                    <p>⚠️ Для исследовательских целей. Не является медицинским устройством.</p>
                    <p>© 2024 AutoAngioScore | Инновационная оценка коронарного поражения</p>
                </div>
            ''')
        
        # ==================== ЛОГИКА ====================
        studies_state = gr.State([])
        
        def _add_study_fn(studies: List[Dict[str, Any]], name: str, desc: str, files, folder):
            name = (name or "").strip() or f"Исследование_{len(studies)+1}"
            desc = (desc or "").strip()
            paths = _collect_input_paths(files, folder)
            
            if not paths:
                table = _update_status_table(studies, "Queued")
                return studies, table, name, desc, files, folder
            
            new_study = {
                "name": name,
                "description": desc,
                "files": paths
            }
            studies = studies + [new_study]
            table = _update_status_table(studies, "Queued")
            return studies, table, "", "", None, None
        
        btn_add.click(
            _add_study_fn,
            inputs=[studies_state, study_name, study_desc, files_all, files_folder],
            outputs=[studies_state, queue_table, study_name, study_desc, files_all, files_folder]
        )
        
        def _clear_form():
            return "", "", None, None
        
        btn_clear.click(_clear_form, inputs=None, outputs=[study_name, study_desc, files_all, files_folder])
        
        def _clear_all():
            return [], _update_status_table([], "Queued")
        
        # Добавляем кнопку очистки очереди (скрытая функциональность)
        with gr.Row(visible=False):
            clear_queue = gr.Button("Очистить очередь")
            clear_queue.click(_clear_all, inputs=None, outputs=[studies_state, queue_table])
        
        def _before_run(studies):
            return _update_status_table(studies, "Running")
        
        def _run_infer(studies):
            start_time = time.time()
            
            study_objs = []
            for s in (studies or []):
                study_objs.append(Study(name=s["name"], description=s.get("description", ""), files=s["files"]))
            
            result = run_inference(study_objs)
            duration_ms = (time.time() - start_time) * 1000
            result['duration_ms'] = duration_ms
            
            # ========== СОХРАНЕНИЕ В БАЗУ ДАННЫХ ==========
            db_manager = get_db_manager()
            if db_manager.check_connection():
                try:
                    for idx, study_data in enumerate(studies):
                        study_name_val = study_data.get("name", f"Study_{idx}")
                        
                        # Получаем ORM-запись исследования и работаем уже с внутренним PK.
                        study_record = db_manager.create_study(
                            study_id=study_name_val,
                            description=study_data.get("description", "")
                        )
                        study_db_id = study_record.id if study_record else None
                        
                        if study_db_id and idx < len(result.get('studies', [])):
                            study_result = result['studies'][idx]
                            
                            # Сохраняем DICOM файлы
                            for file_info in study_result.get('left', {}).get('files', []):
                                file_path = file_info.get('path', '')
                                metadata = extract_dicom_metadata(file_path)
                                db_manager.add_dicom_file(
                                    study_id=study_db_id,
                                    file_path=file_path,
                                    file_name=os.path.basename(file_path),
                                    artery_class='left',
                                    artery_prob=file_info.get('artery_prob', 0.0),
                                    **metadata
                                )
                            
                            for file_info in study_result.get('right', {}).get('files', []):
                                file_path = file_info.get('path', '')
                                metadata = extract_dicom_metadata(file_path)
                                db_manager.add_dicom_file(
                                    study_id=study_db_id,
                                    file_path=file_path,
                                    file_name=os.path.basename(file_path),
                                    artery_class='right',
                                    artery_prob=file_info.get('artery_prob', 0.0),
                                    **metadata
                                )
                            
                            for file_info in study_result.get('other', []):
                                file_path = file_info.get('path', '')
                                metadata = extract_dicom_metadata(file_path)
                                db_manager.add_dicom_file(
                                    study_id=study_db_id,
                                    file_path=file_path,
                                    file_name=os.path.basename(file_path),
                                    artery_class='other',
                                    artery_prob=file_info.get('artery_prob', 0.0),
                                    **metadata
                                )
                            
                            # Сохраняем результат
                            db_manager.save_inference_result(study_db_id, study_result)
                    
                    print("✅ Results saved to PostgreSQL database")
                except Exception as e:
                    print(f"⚠️ Warning: Could not save to database: {e}")
            else:
                print("⚠️ No database connection, results not saved")
            
            report_path = _build_report_file(result)
            return result, report_path
        
        def _after_run(studies, result, report_path):
            table = _update_status_table(studies, "Done")
            return _format_results_html(result), result, report_path, table
        
        run_btn.click(
            _before_run,
            inputs=[studies_state],
            outputs=[queue_table]
        ).then(
            _run_infer,
            inputs=[studies_state],
            outputs=[out_json, out_report]
        ).then(
            _after_run,
            inputs=[studies_state, out_json, out_report],
            outputs=[out_summary, out_json, out_report, queue_table]
        )
    
    return demo


if __name__ == "__main__":
    favicon = LOGO_PATH if (LOGO_PATH and os.path.exists(LOGO_PATH)) else None
    
    # Ждём и инициализируем базу данных
    if wait_for_database():
        try:
            db_manager = get_db_manager()
            db_manager.init_db_if_not_exists()
            print("✅ База данных инициализирована")
        except Exception as e:
            print(f"⚠️ Ошибка инициализации БД: {e}")
    else:
        print("⚠️ Работаем без сохранения результатов в БД")
    
    print("="*50)
    print("🚀 Запуск AutoAngioScore...")
    print("="*50 + "\n")
    
    demo = create_ui()
    demo.launch(
        favicon_path=favicon,
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        css=APPLE_STYLE_CSS
    )