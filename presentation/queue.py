from typing import List, Dict


def status_badge_html(state: str, with_animation: bool = False) -> str:
    """Генерация HTML для статусного бейджа."""
    state = state.lower()

    status_config = {
        "running": {"class": "status-running", "icon": "⏱️", "text": "Выполняется"},
        "done": {"class": "status-done", "icon": "✅", "text": "Завершено"},
        "error": {"class": "status-error", "icon": "❌", "text": "Ошибка"},
        "queued": {"class": "status-queued", "icon": "⏳", "text": "В очереди"},
    }

    config = status_config.get(state, status_config["queued"])
    animation_class = " pulse" if with_animation and state == "running" else ""

    return (
        f'<span class="status-badge {config["class"]}{animation_class}">' 
        f"{config['icon']} {config['text']}" 
        "</span>"
    )


def render_queue_table(studies: List[Dict], status: str) -> str:
    """Рендер HTML таблицы очереди исследований."""
    studies = studies or []

    if not studies:
        return (
            '<div class="apple-card" style="padding: 1rem; text-align: center;">'
            '<div style="color: var(--text-secondary); font-size: 0.875rem;">'
            "Очередь пуста"
            "</div>"
            "</div>"
        )

    badge = status_badge_html(status, with_animation=(status == "running"))
    rows_html = []
    for idx, study in enumerate(studies, 1):
        rows_html.append(
            "<tr>"
            f"<td>{idx}</td>"
            f"<td>{study.get('name', '-')}</td>"
            f"<td>{study.get('description', '-') or '-'}</td>"
            f"<td style=\"text-align: center;\">{len(study.get('files', []))}</td>"
            f"<td style=\"text-align: center;\">{badge}</td>"
            "</tr>"
        )

    return (
        '<div style="overflow-x: auto;">'
        '<table class="queue-table">'
        "<thead>"
        "<tr>"
        "<th>#</th>"
        "<th>Исследование</th>"
        "<th>Описание</th>"
        "<th>Файлов</th>"
        "<th>Статус</th>"
        "</tr>"
        "</thead>"
        "<tbody>"
        f"{''.join(rows_html)}"
        "</tbody>"
        "</table>"
        "</div>"
    )
