#!/usr/bin/env python3
"""Проверка содержимого базы данных."""

import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from src.database.db_manager import DatabaseManager
from src.database.models import Study, DicomFile, InferenceResult, ArteryScore


def _fmt_dt(value):
    return value.strftime("%Y-%m-%d %H:%M:%S") if value else "-"


def check_database() -> None:
    """Вывод краткой информации по всем таблицам БД."""
    db_manager = DatabaseManager(auto_init=False)

    print("\n" + "=" * 80)
    print("📊 Проверка содержимого БД")
    print("=" * 80)

    with db_manager.get_session() as session:
        print("\n📌 Таблица studies")
        studies = session.query(Study).all()
        if not studies:
            print("Нет данных")
        for study in studies:
            print(
                f"- id={study.id} | study_id={study.study_id} | files={len(study.dicom_files)} | "
                f"inferences={len(study.inference_results)} | created={_fmt_dt(study.created_at)} | "
                f"updated={_fmt_dt(study.updated_at)}"
            )

        print("\n📄 Таблица dicom_files")
        dicom_files = session.query(DicomFile).order_by(DicomFile.id.desc()).limit(10).all()
        if not dicom_files:
            print("Нет данных")
        for item in dicom_files:
            print(
                f"- id={item.id} | study_id={item.study_id} | file={item.file_name} | "
                f"artery={item.artery_classification} | prob={item.artery_probability} | "
                f"created={_fmt_dt(item.created_at)}"
            )

        print("\n📈 Таблица inference_results")
        inferences = session.query(InferenceResult).order_by(InferenceResult.id.desc()).limit(10).all()
        if not inferences:
            print("Нет данных")
        for item in inferences:
            print(
                f"- id={item.id} | study_id={item.study_id} | total={item.total_score:.3f} | "
                f"risk={'HIGH' if item.is_high_risk else 'LOW'} | "
                f"date={_fmt_dt(item.inference_date)}"
            )

        print("\n🎯 Таблица artery_scores")
        scores = session.query(ArteryScore).order_by(ArteryScore.id.desc()).limit(10).all()
        if not scores:
            print("Нет данных")
        for item in scores:
            print(
                f"- id={item.id} | result_id={item.inference_result_id} | "
                f"artery={item.artery_type} | score={item.score_value:.3f}"
            )

        stats = db_manager.get_statistics()
        print("\n📊 Статистика")
        print(f"- Всего исследований: {stats['total_studies']}")
        print(f"- Всего результатов: {stats['total_inferences']}")
        print(f"- Средний left: {stats['avg_left_score']:.3f}")
        print(f"- Средний right: {stats['avg_right_score']:.3f}")
        print(f"- Высокий риск: {stats['high_risk_count']} ({stats['high_risk_percentage']:.1f}%)")

        print("\n✅ Проверка завершена")


if __name__ == "__main__":
    try:
        check_database()
    except Exception as exc:
        print(f"\n❌ Ошибка: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
