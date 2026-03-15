"""
SQLite database models for client management, edit jobs, and change tracking.
"""

import os
from datetime import datetime
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float
from sqlalchemy.orm import declarative_base, sessionmaker, Session

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(DATA_DIR, exist_ok=True)

DATABASE_URL = os.environ.get("DATABASE_URL", f"sqlite:///{os.path.join(DATA_DIR, 'app.db')}")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    pool_pre_ping=True
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


class Client(Base):
    __tablename__ = "clients"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    description = Column(Text, default="")
    prompt_content = Column(Text, default="")
    base_content = Column(Text, default="")
    general_prompt_content = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EditJob(Base):
    __tablename__ = "edit_jobs"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, nullable=False, index=True)
    edit_request = Column(Text, nullable=False)
    document_types = Column(Text, default="[]")  # JSON list: ["prompt", "base_de_dados", "prompt_geral"]
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    progress = Column(Integer, default=0)
    error_message = Column(Text, default="")
    summary = Column(Text, default="")
    created_at = Column(DateTime, default=datetime.utcnow)


class EditChange(Base):
    __tablename__ = "edit_changes"

    id = Column(Integer, primary_key=True, index=True)
    job_id = Column(Integer, nullable=False, index=True)
    field = Column(String(50), nullable=False)  # prompt, base_de_dados, prompt_geral
    section = Column(String(255), default="")
    before_text = Column(Text, default="")
    after_text = Column(Text, default="")
    reason = Column(Text, default="")
    status = Column(String(50), default="pending")  # pending, approved, rejected
    created_at = Column(DateTime, default=datetime.utcnow)


class CreationProject(Base):
    """Project for prompt creation pipeline."""
    __tablename__ = "creation_projects"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, nullable=True, index=True)  # Optional link to client
    name = Column(String(255), nullable=False)
    status = Column(String(50), default="collecting")  # collecting, analyzing, gaps, generating, completed
    # Collected data
    onboarding_data = Column(Text, default="{}")  # JSON onboarding form
    scraping_text = Column(Text, default="")
    scraping_url = Column(String(500), default="")
    uploaded_files_text = Column(Text, default="")  # Combined parsed text
    whatsapp_text = Column(Text, default="")
    consolidated_text = Column(Text, default="")
    # User notes/context
    user_notes = Column(Text, default="")
    # Collection logs
    collection_log = Column(Text, default="[]")  # JSON array of log entries
    # Progress tracking
    progress = Column(Integer, default=0)
    # Gap analysis
    gap_analysis_json = Column(Text, default="[]")
    gap_answers_json = Column(Text, default="{}")
    # Generated output
    generated_prompt = Column(Text, default="")
    generated_base = Column(Text, default="")
    generated_general = Column(Text, default="")
    # Meta
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class EditHistory(Base):
    """Legacy table - kept for backward compatibility."""
    __tablename__ = "edit_history"

    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, nullable=False, index=True)
    document_type = Column(String(50), nullable=False)
    original_content = Column(Text, default="")
    edited_content = Column(Text, default="")
    analysis_json = Column(Text, default="{}")
    validation_json = Column(Text, default="{}")
    score = Column(Integer, default=0)
    iterations = Column(Integer, default=0)
    success = Column(Integer, default=0)
    diff_text = Column(Text, default="")
    cost_total = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db():
    Base.metadata.create_all(bind=engine)
