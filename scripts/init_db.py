#!/usr/bin/env python3
"""Script to initialize the PostgreSQL database"""

import sys
import os
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from src.database.db_manager import DatabaseManager

def wait_for_db(max_retries=30, delay=2):
    """Ожидание готовности PostgreSQL"""
    db_manager = DatabaseManager()
    
    for attempt in range(max_retries):
        try:
            with db_manager.get_session() as session:
                # Используем text() для raw SQL
                result = session.execute(text("SELECT 1"))
                if result.scalar() == 1:
                    print("✅ Database is ready!")
                    return True
        except Exception as e:
            print(f"⏳ Waiting for database... (attempt {attempt + 1}/{max_retries})")
            print(f"   Error: {str(e)[:100]}")
            time.sleep(delay)
    
    print("❌ Database connection timeout")
    return False

def main():
    print("🚀 Initializing AutoAngioScore Database...")
    
    # Wait for DB to be ready
    if not wait_for_db():
        print("❌ Could not connect to database. Is Docker running?")
        print("   Run: docker-compose up -d")
        sys.exit(1)
    
    db_manager = DatabaseManager()
    
    try:
        # Create all tables
        db_manager.init_db(drop_first=False)
        print("✅ Database tables created successfully!")
        
        # Test connection and show version
        with db_manager.get_session() as session:
            result = session.execute(text("SELECT version()"))
            version = result.scalar()
            print(f"📦 PostgreSQL version: {version.split(',')[0] if version else 'unknown'}")
            
            # Show created tables
            result = session.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
                ORDER BY table_name
            """))
            tables = [row[0] for row in result.fetchall()]
            if tables:
                print(f"📋 Created tables: {', '.join(tables)}")
            else:
                print("📋 No tables found (they will be created when app runs)")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()