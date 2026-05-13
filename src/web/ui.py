import os
import time
from typing import Any, Dict, List

import gradio as gr

from src.database.db_manager import get_db_manager
from src.syntax_pred.infer import Study, run_inference, extract_dicom_metadata

from .assets import logo_html
from .files import collect_input_paths
from .queue import render_queue_table
from .report import build_report_file
from .results import format_results_html


def create_ui() -> gr.Blocks:
    """Создание интерфейса в стиле Apple."""
    with gr.Blocks(title="AutoAngioScore") as demo:

        with gr.Column(elem_classes="apple-container"):

            with gr.Row(elem_classes="apple-header"):
                with gr.Column(scale=1, min_width=0):
                    logo = logo_html()
                    if logo:
                        gr.HTML(f'<div style="margin-bottom: 1rem;">{logo}</div>')

                    gr.HTML('''
                        <h1 class="apple-title">AutoAngioScore</h1>
                        <p class="apple-subtitle">Автоматическая оценка степени коронарного поражения по видеозаписям ангиографии</p>
                    ''')

            with gr.Group(elem_classes="apple-card add-study-card"):
                with gr.Column(elem_classes="apple-card-header"):
                    gr.HTML('<h3 class="apple-card-title">✨ Добавление нового исследования</h3>')

                with gr.Column(elem_classes="apple-card-content"):
                    with gr.Row():
                        study_name = gr.Textbox(
                            label="Идентификатор исследования",
                            placeholder="Например: INV-2024-001",
                            elem_classes="apple-input",
                            scale=1,
                        )
                        study_desc = gr.Textbox(
                            label="Описание (необязательно)",
                            placeholder="Клинические данные, особенности...",
                            elem_classes="apple-input",
                            scale=1,
                        )

                    gr.HTML('<div class="upload-grid">')

                    with gr.Column(elem_classes="apple-card", variant="panel"):
                        with gr.Column(elem_classes="apple-card-header"):
                            gr.HTML('<h3 class="apple-card-title" style="font-size: 1rem;">📄 Отдельные файлы</h3>')

                        with gr.Column(elem_classes="apple-card-content"):
                            files_all = gr.File(
                                label="Выберите DICOM файлы",
                                file_count="multiple",
                                elem_classes="apple-input",
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
                                elem_classes="apple-input",
                            )
                            gr.HTML('''
                                <div style="font-size: 0.75rem; color: var(--text-secondary); margin-top: 0.5rem;">
                                    ✓ Выберите папку, содержащую DICOM файлы
                                </div>
                            ''')

                    gr.HTML('</div>')

                    with gr.Row():
                        btn_add = gr.Button(
                            "✨ Добавить в очередь",
                            elem_classes="apple-button-add",
                            scale=1,
                        )
                        btn_clear = gr.Button(
                            "🗑️ Очистить форму",
                            elem_classes="apple-button-clear",
                            scale=1,
                        )

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

            with gr.Group(elem_classes="apple-card"):
                with gr.Column(elem_classes="apple-card-header"):
                    gr.HTML('<h3 class="apple-card-title">📋 Очередь исследований</h3>')

                with gr.Column(elem_classes="apple-card-content"):
                    queue_table = gr.HTML(
                        value=render_queue_table([], "Queued"),
                        elem_classes="apple-table",
                    )

                    gr.HTML('''
                        <div style="font-size: 0.8125rem; color: var(--text-secondary); margin-top: 0.75rem; text-align: center;">
                            💡 Добавьте исследования в очередь для пакетного анализа
                        </div>
                    ''')

            with gr.Row():
                run_btn = gr.Button(
                    "🚀 Запустить анализ очереди",
                    elem_classes="apple-button",
                )

            with gr.Group(elem_classes="apple-card"):
                with gr.Column(elem_classes="apple-card-header"):
                    gr.HTML('<h3 class="apple-card-title">📊 Результаты анализа</h3>')

                with gr.Column(elem_classes="apple-card-content"):
                    out_summary = gr.HTML(label="")
                    out_json = gr.JSON(label="Подробные данные", visible=False)

                    with gr.Row():
                        out_report = gr.File(
                            label="📥 Скачать отчет JSON",
                            interactive=False,
                            elem_classes="apple-input",
                        )

            gr.HTML('''
                <div style="margin-top: 3rem; padding-top: 1.5rem; border-top: 1px solid rgba(255,255,255,0.15); text-align: center; font-size: 0.75rem; color: rgba(255,255,255,0.7);">
                    <p>⚠️ Для исследовательских целей. Не является медицинским устройством.</p>
                    <p>© 2024 AutoAngioScore | Инновационная оценка коронарного поражения</p>
                </div>
            ''')

        studies_state = gr.State([])

        def add_study(studies: List[Dict[str, Any]], name: str, desc: str, files, folder):
            name = (name or "").strip() or f"Исследование_{len(studies) + 1}"
            desc = (desc or "").strip()
            paths = collect_input_paths(files, folder)

            if not paths:
                table = render_queue_table(studies, "Queued")
                return studies, table, name, desc, files, folder

            new_study = {
                "name": name,
                "description": desc,
                "files": paths,
            }
            studies = studies + [new_study]
            table = render_queue_table(studies, "Queued")
            return studies, table, "", "", None, None

        btn_add.click(
            add_study,
            inputs=[studies_state, study_name, study_desc, files_all, files_folder],
            outputs=[studies_state, queue_table, study_name, study_desc, files_all, files_folder],
        )

        def clear_form():
            return "", "", None, None

        btn_clear.click(clear_form, inputs=None, outputs=[study_name, study_desc, files_all, files_folder])

        def clear_all():
            return [], render_queue_table([], "Queued")

        with gr.Row(visible=False):
            clear_queue = gr.Button("Очистить очередь")
            clear_queue.click(clear_all, inputs=None, outputs=[studies_state, queue_table])

        def before_run(studies):
            return render_queue_table(studies, "Running")

        def run_infer(studies):
            start_time = time.time()

            study_objs = []
            for study in (studies or []):
                study_objs.append(Study(name=study["name"], description=study.get("description", ""), files=study["files"]))

            result = run_inference(study_objs)
            duration_ms = (time.time() - start_time) * 1000
            result["duration_ms"] = duration_ms

            db_manager = get_db_manager()
            if db_manager.check_connection():
                try:
                    for idx, study_data in enumerate(studies):
                        study_name_val = study_data.get("name", f"Study_{idx}")

                        study_record = db_manager.create_study(
                            study_id=study_name_val,
                            description=study_data.get("description", ""),
                        )
                        study_db_id = study_record.id if study_record else None

                        if study_db_id and idx < len(result.get("studies", [])):
                            study_result = result["studies"][idx]

                            for file_info in study_result.get("left", {}).get("files", []):
                                file_path = file_info.get("path", "")
                                metadata = extract_dicom_metadata(file_path)
                                db_manager.add_dicom_file(
                                    study_id=study_db_id,
                                    file_path=file_path,
                                    file_name=os.path.basename(file_path),
                                    artery_class="left",
                                    artery_prob=file_info.get("artery_prob", 0.0),
                                    **metadata,
                                )

                            for file_info in study_result.get("right", {}).get("files", []):
                                file_path = file_info.get("path", "")
                                metadata = extract_dicom_metadata(file_path)
                                db_manager.add_dicom_file(
                                    study_id=study_db_id,
                                    file_path=file_path,
                                    file_name=os.path.basename(file_path),
                                    artery_class="right",
                                    artery_prob=file_info.get("artery_prob", 0.0),
                                    **metadata,
                                )

                            for file_info in study_result.get("other", []):
                                file_path = file_info.get("path", "")
                                metadata = extract_dicom_metadata(file_path)
                                db_manager.add_dicom_file(
                                    study_id=study_db_id,
                                    file_path=file_path,
                                    file_name=os.path.basename(file_path),
                                    artery_class="other",
                                    artery_prob=file_info.get("artery_prob", 0.0),
                                    **metadata,
                                )

                            db_manager.save_inference_result(study_db_id, study_result)

                    print("✅ Результаты сохранены в PostgreSQL")
                except Exception as exc:
                    print(f"⚠️ Не удалось сохранить результаты в БД: {exc}")
            else:
                print("⚠️ Нет подключения к БД, результаты не сохраняются")

            report_path = build_report_file(result)
            return result, report_path

        def after_run(studies, result, report_path):
            table = render_queue_table(studies, "Done")
            return format_results_html(result), result, report_path, table

        run_btn.click(
            before_run,
            inputs=[studies_state],
            outputs=[queue_table],
        ).then(
            run_infer,
            inputs=[studies_state],
            outputs=[out_json, out_report],
        ).then(
            after_run,
            inputs=[studies_state, out_json, out_report],
            outputs=[out_summary, out_json, out_report, queue_table],
        )

    return demo
