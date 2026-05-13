import os
import time

from sqlalchemy import text

from infrastructure.database.db_manager import get_db_manager
from presentation.assets import LOGO_PATH
from presentation.styles import APPLE_STYLE_CSS
from presentation.ui import create_ui


def wait_for_database(max_retries: int = 30, delay: int = 2) -> bool:
    print("\n" + "=" * 50)
    print("🔍 Проверка подключения к PostgreSQL...")
    print("=" * 50)

    for attempt in range(max_retries):
        try:
            db_manager = get_db_manager()
            with db_manager.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                print("✅ PostgreSQL готов к работе!")
                return True
        except Exception:
            print(f"⏳ Ожидание PostgreSQL... (попытка {attempt + 1}/{max_retries})")
            time.sleep(delay)

    print("⚠️ PostgreSQL не доступен, продолжаем без сохранения в БД")
    return False


def run_app() -> None:
    favicon = LOGO_PATH if (LOGO_PATH and os.path.exists(LOGO_PATH)) else None

    if wait_for_database():
        try:
            db_manager = get_db_manager()
            db_manager.init_db_if_not_exists()
            print("✅ База данных инициализирована")
        except Exception as exc:
            print(f"⚠️ Ошибка инициализации БД: {exc}")
    else:
        print("⚠️ Работаем без сохранения результатов в БД")

    print("=" * 50)
    print("🚀 Запуск AutoAngioScore...")
    print("=" * 50 + "\n")

    demo = create_ui()
    demo.launch(
        favicon_path=favicon,
        server_name="0.0.0.0",
        server_port=7860,
        share=False,
        css=APPLE_STYLE_CSS,
    )