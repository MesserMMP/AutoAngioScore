import os
from typing import Any, Dict, List


def format_results_html(result: Dict[str, Any]) -> str:
    """Форматирование результатов в HTML с детальной информацией."""
    if not result:
        return (
            '<div class="apple-card" style="padding: 2rem; text-align: center;">'
            '<div style="color: var(--text-secondary);">'
            "📊 Результаты появятся после запуска анализа"
            "</div>"
            "</div>"
        )

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
        return (
            '<div class="apple-card" style="padding: 2rem; text-align: center;">'
            '<div style="color: var(--text-secondary);">'
            "📋 Нет исследований для отображения"
            "</div>"
            "</div>"
        )

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

    cards_html: List[str] = [accordion_styles]

    for idx, study in enumerate(studies):
        study_name = study.get("study", "-")
        description = study.get("description", "")
        unique_id = f"details_{idx}_{study_name.replace(' ', '_').replace('/', '_')}"

        left_data = study.get("left", {})
        right_data = study.get("right", {})
        other_data = study.get("other", [])
        total_obj = study.get("total", {})

        left_mean = left_data.get("mean", 0.0)
        right_mean = right_data.get("mean", 0.0)
        total_mean = total_obj.get("mean", 0.0)

        left_files_count = left_data.get("n_files", 0)
        right_files_count = right_data.get("n_files", 0)
        other_files_count = len(other_data)

        left_per_model = left_data.get("per_model", [])
        right_per_model = right_data.get("per_model", [])

        risk_key = next((key for key in total_obj.keys() if "High-risk" in str(key)), None)
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
            left_models_html += "</div>"
        else:
            left_models_html = (
                '<div style="margin-top: 8px; font-size: 11px; color: var(--text-light); text-align: center;">'
                "Нет данных моделей"
                "</div>"
            )

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
            right_models_html += "</div>"
        else:
            right_models_html = (
                '<div style="margin-top: 8px; font-size: 11px; color: var(--text-light); text-align: center;">'
                "Нет данных моделей"
                "</div>"
            )

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
            left_files_html += "</div>"
        else:
            left_files_html = (
                '<div style="margin-top: 8px; font-size: 11px; color: var(--text-light); text-align: center;">'
                "Нет файлов"
                "</div>"
            )

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
            right_files_html += "</div>"
        else:
            right_files_html = (
                '<div style="margin-top: 8px; font-size: 11px; color: var(--text-light); text-align: center;">'
                "Нет файлов"
                "</div>"
            )

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
            other_files_html += "</div>"
        else:
            other_files_html = (
                '<div style="margin-top: 8px; font-size: 11px; color: var(--text-light); text-align: center;">'
                "Нераспознанных файлов нет"
                "</div>"
            )

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

                <details id="{unique_id}" class="detail-accordion">
                    <summary>
                        <div class="detail-button">
                            <span class="toggle-icon-open">▼</span>
                            <span class="toggle-icon-close">▲</span>
                            <span class="toggle-text-open">Показать детальную информацию</span>
                            <span class="toggle-text-close">Скрыть детальную информацию</span>
                        </div>
                    </summary>

                    <div style="margin-top: 1.5rem;">

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

                        <div style="background: rgba(6,182,212,0.03); border-radius: 12px; padding: 0.75rem; margin-bottom: 0.75rem; border: 1px solid rgba(6,182,212,0.1);">
                            <div style="font-size: 0.75rem; font-weight: 700; color: #06b6d4; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                                <span>📂</span> Файлы левой артерии (вероятность ≤ 0.10)
                                <span style="background: #06b6d4; color: white; padding: 0 6px; border-radius: 12px; font-size: 9px;">{left_files_count}</span>
                            </div>
                            {left_files_html}
                        </div>

                        <div style="background: rgba(139,92,246,0.03); border-radius: 12px; padding: 0.75rem; margin-bottom: 0.75rem; border: 1px solid rgba(139,92,246,0.1);">
                            <div style="font-size: 0.75rem; font-weight: 700; color: #8b5cf6; margin-bottom: 0.5rem; display: flex; align-items: center; gap: 0.5rem;">
                                <span>📂</span> Файлы правой артерии (вероятность ≥ 0.90)
                                <span style="background: #8b5cf6; color: white; padding: 0 6px; border-radius: 12px; font-size: 9px;">{right_files_count}</span>
                            </div>
                            {right_files_html}
                        </div>

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

                <div style="margin-top: 1rem; padding-top: 0.75rem; border-top: 1px solid rgba(0,0,0,0.05); display: flex; justify-content: space-between; font-size: 0.65rem; color: var(--text-light);">
                    <span>🎯 Порог высокого риска SYNTAX: ≥22.0</span>
                    <span>🧠 Ансамбль моделей: {len(left_per_model)} левых / {len(right_per_model)} правых</span>
                </div>
            </div>
        </div>
        '''
        cards_html.append(card_html)

    return "".join(cards_html)
