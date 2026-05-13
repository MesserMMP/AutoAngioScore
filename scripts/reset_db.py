#!/usr/bin/env python3
"""Полный сброс БД (удаление таблиц и создание заново)."""

import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, inspect
from src.database.db_manager import DatabaseManager
from src.database.models import Base


def reset_database() -> bool:
    """Сброс БД с удалением всех таблиц и созданием схемы заново."""
    db_manager = DatabaseManager(auto_init=False)

    print("\n" + "=" * 80)
    print("🔄 Полный сброс БД")
    print("=" * 80)
    print("\n⚠️ Это удалит все данные из БД!")
    response = input("Продолжить? (yes/no): ").strip().lower()
    if response != "yes":
        print("Отменено")
        return False

    if not db_manager.check_connection():
        print("❌ Не удалось подключиться к БД")
        return False

    print("\n🗑️ Удаляем все таблицы...")
    try:
        with db_manager.engine.connect() as conn:
            inspector = inspect(db_manager.engine)
            existing_tables = inspector.get_table_names()

            print(f"Найдены таблицы: {', '.join(existing_tables)}")

            for table_name in existing_tables:
                print(f"  Удаляем: {table_name}")
                conn.execute(text(f"DROP TABLE IF EXISTS {table_name} CASCADE"))
                conn.commit()

            print("✓ Все таблицы удалены")
    except Exception as exc:
        print(f"❌ Ошибка удаления таблиц: {exc}")
        return False

    print("\n📝 Создаем новую схему...")
    try:
        Base.metadata.create_all(bind=db_manager.engine)
        print("✓ Схема успешно создана")
    except Exception as exc:
        print(f"❌ Ошибка создания схемы: {exc}")
        return False

    print("\n" + "=" * 80)
    print("✅ Сброс БД завершен!")
    print("=" * 80 + "\n")

    return True


if __name__ == "__main__":
    try:
        if reset_database():
            sys.exit(0)
        sys.exit(1)
    except Exception as exc:
        print(f"\n❌ Ошибка: {exc}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
