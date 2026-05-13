"""SQLAlchemy models for PostgreSQL database"""

from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, Text, ForeignKey, 
    JSON, Boolean, Index, UniqueConstraint
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import inspect

Base = declarative_base()

class Study(Base):
    """Модель исследования (пациент/исследование)"""
    __tablename__ = 'studies'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    study_id = Column(String(255), nullable=False, index=True)  # Внешний ID (больше не уникален для дубликатов)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Связи
    dicom_files = relationship("DicomFile", back_populates="study", cascade="all, delete-orphan")
    inference_results = relationship("InferenceResult", back_populates="study", cascade="all, delete-orphan")
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'study_id': self.study_id,
            'description': self.description,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }


class DicomFile(Base):
    """Модель DICOM файла с метаданными"""
    __tablename__ = 'dicom_files'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    study_id = Column(Integer, ForeignKey('studies.id', ondelete='CASCADE'), nullable=False)
    file_path = Column(String(1024), nullable=False)
    file_name = Column(String(255), nullable=False)
    series_uid = Column(String(255), nullable=True, index=True)  # SeriesInstanceUID
    sop_uid = Column(String(255), nullable=True)  # SOPInstanceUID
    patient_id = Column(String(255), nullable=True)
    study_uid = Column(String(255), nullable=True)
    modality = Column(String(50), nullable=True)
    series_number = Column(Integer, nullable=True)
    instance_number = Column(Integer, nullable=True)
    artery_classification = Column(String(20), nullable=True)  # 'left', 'right', 'other'
    artery_probability = Column(Float, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Связи
    study = relationship("Study", back_populates="dicom_files")
    
    __table_args__ = (
        Index('idx_study_series', 'study_id', 'series_uid'),
    )
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'file_name': self.file_name,
            'series_uid': self.series_uid,
            'artery_classification': self.artery_classification,
            'artery_probability': self.artery_probability,
        }


class InferenceResult(Base):
    """Модель результата инференса для исследования"""
    __tablename__ = 'inference_results'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    study_id = Column(Integer, ForeignKey('studies.id', ondelete='CASCADE'), nullable=False)
    inference_date = Column(DateTime, default=datetime.utcnow, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)  # Когда запись добавлена в БД
    
    # Основные результаты
    left_score = Column(Float, nullable=False, default=0.0)
    right_score = Column(Float, nullable=False, default=0.0)
    total_score = Column(Float, nullable=False, default=0.0)
    is_high_risk = Column(Boolean, nullable=False, default=False)
    
    # Детальная информация
    left_files_count = Column(Integer, default=0)
    right_files_count = Column(Integer, default=0)
    other_files_count = Column(Integer, default=0)
    
    # JSON поля для расширенных данных
    left_per_model_scores = Column(JSON, nullable=True)  # [{model: str, score: float}]
    right_per_model_scores = Column(JSON, nullable=True)
    other_files_info = Column(JSON, nullable=True)  # [{path: str, artery_prob: float}]
    
    # Конфигурация модели
    model_config = Column(JSON, nullable=True)  # Сохраняем CFG параметры
    
    # Время выполнения
    inference_duration_ms = Column(Float, nullable=True)
    
    # Связи
    study = relationship("Study", back_populates="inference_results")
    artery_scores = relationship("ArteryScore", back_populates="inference_result", cascade="all, delete-orphan")
    
    __table_args__ = (
        Index('idx_study_inference_date', 'study_id', 'inference_date'),
        Index('idx_total_score', 'total_score'),
    )
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'inference_date': self.inference_date.isoformat() if self.inference_date else None,
            'left_score': self.left_score,
            'right_score': self.right_score,
            'total_score': self.total_score,
            'is_high_risk': self.is_high_risk,
            'left_files_count': self.left_files_count,
            'right_files_count': self.right_files_count,
            'other_files_count': self.other_files_count,
        }


class ArteryScore(Base):
    """Модель детальных оценок для каждой артерии (можно расширить)"""
    __tablename__ = 'artery_scores'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    inference_result_id = Column(Integer, ForeignKey('inference_results.id', ondelete='CASCADE'), nullable=False)
    artery_type = Column(String(10), nullable=False)  # 'left' or 'right'
    model_name = Column(String(255), nullable=True)
    score_value = Column(Float, nullable=False)
    
    # Связи
    inference_result = relationship("InferenceResult", back_populates="artery_scores")
    
    __table_args__ = (
        Index('idx_inference_artery', 'inference_result_id', 'artery_type'),
    )
    
    def to_dict(self) -> dict:
        return {
            'artery_type': self.artery_type,
            'model_name': self.model_name,
            'score_value': self.score_value,
        }