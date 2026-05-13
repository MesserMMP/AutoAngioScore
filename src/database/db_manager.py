"""Database manager for AutoAngioScore with auto-initialization"""

import os
import time
from typing import List, Dict, Any, Optional
from datetime import datetime
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from dotenv import load_dotenv
from sqlalchemy import inspect

from .models import Base, Study, DicomFile, InferenceResult, ArteryScore

# Load environment variables
load_dotenv()

class DatabaseManager:
    """Менеджер для работы с PostgreSQL с автоматической инициализацией"""
    
    def __init__(self, db_url: Optional[str] = None, auto_init: bool = True):
        """
        Инициализация менеджера БД
        
        Args:
            db_url: URL подключения к БД (опционально, можно через env)
            auto_init: Автоматически инициализировать таблицы при подключении
        """
        if db_url is None:
            db_url = self._get_db_url_from_env()
        
        self.db_url = db_url
        self.engine = create_engine(
            db_url,
            pool_pre_ping=True,
            pool_recycle=3600,
            echo=False  # Set to True for SQL debugging
        )
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
            bind=self.engine,
        )
        
        if auto_init:
            self.init_db_if_not_exists()
    
    def _get_db_url_from_env(self) -> str:
        """Получить URL БД из переменных окружения"""
        host = os.getenv('DB_HOST', 'localhost')
        port = os.getenv('DB_PORT', '5432')
        db_name = os.getenv('DB_NAME', 'autoangioscore')
        user = os.getenv('DB_USER', 'postgres')
        password = os.getenv('DB_PASSWORD', 'postgres')
        
        return f"postgresql://{user}:{password}@{host}:{port}/{db_name}"
    
    def wait_for_db(self, max_retries: int = 30, delay: int = 2) -> bool:
        """Ожидание готовности PostgreSQL"""
        for attempt in range(max_retries):
            try:
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                    print(f"✅ Database connection established (attempt {attempt + 1})")
                    return True
            except OperationalError as e:
                print(f"⏳ Waiting for database... (attempt {attempt + 1}/{max_retries})")
                time.sleep(delay)
            except Exception as e:
                print(f"⚠️ Unexpected error: {e}")
                time.sleep(delay)
        
        print("❌ Could not connect to database after maximum retries")
        return False
    
    def init_db_if_not_exists(self, drop_first: bool = False):
        """Инициализация таблиц БД, если они не существуют"""
        try:
            inspector = inspect(self.engine)
            existing_tables = inspector.get_table_names()

            if drop_first:
                Base.metadata.drop_all(bind=self.engine)
                existing_tables = []

            expected_tables = sorted(Base.metadata.tables.keys())
            missing_tables = [table for table in expected_tables if table not in existing_tables]

            if existing_tables:
                print(f"ℹ️ Existing tables: {', '.join(sorted(existing_tables))}")
            if missing_tables:
                print(f"ℹ️ Missing tables will be created: {', '.join(missing_tables)}")

            Base.metadata.create_all(bind=self.engine)
            print("✅ Database tables created successfully!")

            inspector = inspect(self.engine)
            tables = inspector.get_table_names()
            print(f"📋 Created tables: {', '.join(tables)}")
            
        except Exception as e:
            print(f"⚠️ Warning: Could not initialize database: {e}")
    
    def check_connection(self) -> bool:
        """Проверить соединение с БД"""
        try:
            with self.engine.connect() as conn:
                conn.execute(text("SELECT 1"))
                return True
        except Exception:
            return False
    
    @contextmanager
    def get_session(self) -> Session:
        """Контекстный менеджер для сессии БД"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()

    def _coerce_study_id(self, study_or_id: Any) -> Optional[int]:
        """Нормализовать входной study_id до целого числа."""
        if isinstance(study_or_id, Study):
            return study_or_id.id
        if isinstance(study_or_id, int):
            return study_or_id
        if hasattr(study_or_id, "id"):
            value = getattr(study_or_id, "id")
            return int(value) if value is not None else None
        return None

    def _filter_model_kwargs(self, model, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Оставить только поля, которые реально есть в модели."""
        valid_columns = set(inspect(model).mapper.columns.keys())
        return {key: value for key, value in payload.items() if key in valid_columns}
    
    # ========== CRUD for Studies ==========
    
    def create_study(self, study_id: str, description: str = "") -> Optional[Study]:
        """Создать новое исследование"""
        with self.get_session() as session:
            try:
                existing = session.query(Study).filter(Study.study_id == study_id).first()
                if existing:
                    session.refresh(existing)
                    return existing
                
                study = Study(
                    study_id=study_id,
                    description=description
                )
                session.add(study)
                session.flush()
                session.refresh(study)
                return study
            except SQLAlchemyError as e:
                print(f"❌ Error creating study: {e}")
                return None
    
    def get_study(self, study_id: str) -> Optional[Study]:
        """Получить исследование по ID"""
        with self.get_session() as session:
            return session.query(Study).filter(Study.study_id == study_id).first()
    
    def get_study_by_id(self, study_id_int: int) -> Optional[Study]:
        """Получить исследование по внутреннему ID"""
        with self.get_session() as session:
            return session.query(Study).filter(Study.id == study_id_int).first()
    
    def get_all_studies(self, limit: int = 100) -> List[Study]:
        """Получить список исследований"""
        with self.get_session() as session:
            return session.query(Study).order_by(Study.created_at.desc()).limit(limit).all()
    
    # ========== CRUD for DICOM Files ==========
    
    def add_dicom_file(self, study_id: int, file_path: str, file_name: str, 
                       series_uid: str = None, artery_class: str = None, 
                       artery_prob: float = None, **metadata) -> Optional[DicomFile]:
        """Добавить DICOM файл"""
        with self.get_session() as session:
            try:
                study_pk = self._coerce_study_id(study_id)
                if study_pk is None:
                    print(f"❌ Invalid study_id for DICOM save: {study_id!r}")
                    return None

                payload = self._filter_model_kwargs(DicomFile, metadata)
                dicom_file = DicomFile(
                    study_id=study_pk,
                    file_path=file_path,
                    file_name=file_name,
                    series_uid=series_uid,
                    artery_classification=artery_class,
                    artery_probability=artery_prob,
                    **payload
                )
                session.add(dicom_file)
                session.flush()
                session.refresh(dicom_file)
                return dicom_file
            except SQLAlchemyError as e:
                print(f"❌ Error adding DICOM file: {e}")
                return None
    
    # ========== CRUD for Inference Results ==========
    
    def save_inference_result(self, study_id: int, result_data: Dict[str, Any]) -> Optional[InferenceResult]:
        """Сохранить результат инференса"""
        with self.get_session() as session:
            try:
                study_pk = self._coerce_study_id(study_id)
                if study_pk is None:
                    print(f"❌ Invalid study_id for inference save: {study_id!r}")
                    return None

                study = session.query(Study).filter(Study.id == study_pk).first()
                if not study:
                    print(f"❌ Study with id {study_pk} not found")
                    return None
                
                left_data = result_data.get('left', {})
                right_data = result_data.get('right', {})
                total_data = result_data.get('total', {})
                other_data = result_data.get('other', [])
                
                total_score = total_data.get('mean', 0.0)
                threshold = 22.0
                
                inference_result = InferenceResult(
                    study_id=study_pk,
                    left_score=left_data.get('mean', 0.0),
                    right_score=right_data.get('mean', 0.0),
                    total_score=total_score,
                    is_high_risk=total_score >= threshold,
                    left_files_count=left_data.get('n_files', 0),
                    right_files_count=right_data.get('n_files', 0),
                    other_files_count=len(other_data),
                    left_per_model_scores=left_data.get('per_model', []),
                    right_per_model_scores=right_data.get('per_model', []),
                    other_files_info=other_data,
                    inference_duration_ms=result_data.get('duration_ms', None)
                )
                session.add(inference_result)
                session.flush()
                
                # Add detailed artery scores
                for model_score in left_data.get('per_model', []):
                    artery_score = ArteryScore(
                        inference_result_id=inference_result.id,
                        artery_type='left',
                        model_name=model_score.get('model', 'unknown'),
                        score_value=model_score.get('score', 0.0)
                    )
                    session.add(artery_score)
                
                for model_score in right_data.get('per_model', []):
                    artery_score = ArteryScore(
                        inference_result_id=inference_result.id,
                        artery_type='right',
                        model_name=model_score.get('model', 'unknown'),
                        score_value=model_score.get('score', 0.0)
                    )
                    session.add(artery_score)
                
                session.flush()
                session.refresh(inference_result)
                print(f"✅ Inference result saved for study {study.study_id}")
                return inference_result
                
            except SQLAlchemyError as e:
                print(f"❌ Error saving inference result: {e}")
                return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """Получить общую статистику по БД"""
        from sqlalchemy import func
        
        with self.get_session() as session:
            total_studies = session.query(Study).count()
            total_inferences = session.query(InferenceResult).count()
            
            avg_result = session.query(
                func.avg(InferenceResult.left_score).label('avg_left'),
                func.avg(InferenceResult.right_score).label('avg_right')
            ).first()
            
            high_risk_count = session.query(InferenceResult).filter(
                InferenceResult.is_high_risk == True
            ).count()
            
            return {
                'total_studies': total_studies,
                'total_inferences': total_inferences,
                'avg_left_score': float(avg_result.avg_left) if avg_result.avg_left else 0,
                'avg_right_score': float(avg_result.avg_right) if avg_result.avg_right else 0,
                'high_risk_count': high_risk_count,
                'high_risk_percentage': (high_risk_count / total_inferences * 100) if total_inferences > 0 else 0
            }


# Глобальный экземпляр менеджера БД
_db_manager: Optional[DatabaseManager] = None

def get_db_manager() -> DatabaseManager:
    """Получить глобальный экземпляр менеджера БД (синглтон)"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseManager()
    return _db_manager

def init_database():
    """Инициализировать базу данных (для использования в скриптах)"""
    manager = get_db_manager()
    if manager.wait_for_db():
        manager.init_db_if_not_exists()
        return True
    return False