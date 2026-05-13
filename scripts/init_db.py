#!/usr/bin/env python3
"""Скрипт инициализации PostgreSQL"""

import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from src.database.db_manager import DatabaseManager

def wait_for_db(max_retries=10, delay=2):
    """Ожидание готовности PostgreSQL"""
    db_manager = DatabaseManager(auto_init=False)
    
    for attempt in range(max_retries):
        try:
            with db_manager.get_session() as session:
                result = session.execute(text("SELECT 1"))
                if result.scalar() == 1:
                    print("✅ Подключение к БД установлено!")
                    return True
        except Exception as e:
            print(f"⏳ Ожидание БД... (attempt {attempt + 1}/{max_retries})")
            print(f"   Ошибка: {str(e)[:100]}")
            time.sleep(delay)
    
    print("❌ Таймаут подключения к БД")
    return False

def main():
    print("🚀 Инициализация БД AutoAngioScore...")
    print("=" * 50)
    
    # Wait for DB to be ready
    if not wait_for_db():
        print("❌ Не удалось подключиться к БД.")
        print("   Убедитесь, что PostgreSQL запущен и .env настроен корректно.")
        sys.exit(1)
    
    db_manager = DatabaseManager(auto_init=False)
    
    try:
        # Create all tables using init_db_if_not_exists
        db_manager.init_db_if_not_exists()
        print("✅ Таблицы БД успешно созданы!")
        
        # Test connection and show version
        with db_manager.get_session() as session:
            result = session.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"📦 Версия PostgreSQL: {version.split(',')[0] if version else 'unknown'}")
            
            # Show created tables
            result = session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            if tables:
                print(f"📋 Текущие таблицы: {', '.join(tables)}")
            else:
                print("📋 Таблицы не найдены")
            
    except Exception as e:
        print(f"❌ Ошибка инициализации БД: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n✅ Инициализация БД завершена!")
    print("=" * 50)

if __name__ == "__main__":
    main()