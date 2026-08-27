"""数据库模型 - 使用 Supabase PostgreSQL。"""
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Float, ForeignKey, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from datetime import datetime
import os

# 导入数据库配置
from config.database import get_database_url

DATABASE_URL = get_database_url()

# 创建引擎（PostgreSQL 不需要 check_same_thread）
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    """获取数据库会话。"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """初始化数据库表。"""
    Base.metadata.create_all(bind=engine)
    print(f"Database connected: {DATABASE_URL[:50]}...")

# ─── 项目管理 ───
class Project(Base):
    __tablename__ = "projects"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    client_name = Column(String(100))
    address = Column(String(300))
    area = Column(Float)
    style = Column(String(50))
    budget = Column(String(50))
    status = Column(String(30), default="接洽中")
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    files = relationship("ProjectFile", back_populates="project", cascade="all, delete-orphan")
    notes = relationship("ProjectNote", back_populates="project", cascade="all, delete-orphan")

class ProjectFile(Base):
    __tablename__ = "project_files"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    filename = Column(String(300))
    filepath = Column(String(500))
    file_type = Column(String(30))
    stage = Column(String(30))
    uploaded_at = Column(DateTime, default=datetime.now)
    project = relationship("Project", back_populates="files")

class ProjectNote(Base):
    __tablename__ = "project_notes"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    content = Column(Text, nullable=False)
    note_type = Column(String(30), default="沟通记录")
    created_at = Column(DateTime, default=datetime.now)
    project = relationship("Project", back_populates="notes")

# ─── 客户管理 ───
class Client(Base):
    __tablename__ = "clients"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    phone = Column(String(30))
    wechat = Column(String(100))
    source = Column(String(100))
    budget_range = Column(String(50))
    preferred_style = Column(String(100))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

# ─── 灵感库 ───
class Inspiration(Base):
    __tablename__ = "inspirations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(200))
    description = Column(Text)
    image_path = Column(String(500))
    source_url = Column(String(500))
    tags = Column(JSON)
    category = Column(String(50))
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.now)

# ─── AI 生图记录 ───
class AIGeneration(Base):
    __tablename__ = "ai_generations"
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    prompt = Column(Text, nullable=False)
    negative_prompt = Column(Text)
    style = Column(String(50))
    mode = Column(String(20))
    input_image = Column(String(500))
    output_image = Column(String(500))
    model = Column(String(100))
    parameters = Column(JSON)
    status = Column(String(20), default="pending")
    created_at = Column(DateTime, default=datetime.now)

# ─── Agent 配置 ───
class AgentConfig(Base):
    __tablename__ = "agent_configs"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    display_name = Column(String(100))
    role = Column(String(50))
    system_prompt = Column(Text)
    capabilities = Column(JSON)
    red_lines = Column(JSON)
    autonomy_level = Column(String(20), default="执行")
    status = Column(String(20), default="active")
    created_at = Column(DateTime, default=datetime.now)

# ─── 材料库 ───
class Material(Base):
    __tablename__ = "materials"
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200), nullable=False)
    category = Column(String(50))
    brand = Column(String(100))
    model = Column(String(100))
    spec = Column(String(200))
    unit = Column(String(20))
    price = Column(Float)
    color = Column(String(50))
    texture = Column(String(100))
    image_path = Column(String(500))
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.now)

# ─── 用户认证 ───
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, autoincrement=True)
    phone = Column(String(20), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    name = Column(String(100))
    created_at = Column(DateTime, default=datetime.now)
    last_login = Column(DateTime)
