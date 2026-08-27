"""通过 Supabase REST API 创建表。"""
import requests
import json

# Supabase 配置
SUPABASE_URL = "https://kntzsbpfsbcvbyqttksb.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtudHpzYnBmc2JjdmJ5cXR0a3NiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc4MTQwNzgsImV4cCI6MjEwMzM5MDA3OH0.WHX89yefpdr9iqJ87B8Y9Cnl-sg2SPvnW4uQi8n1hkU"

# SQL 语句
SQL = """
-- 项目表
CREATE TABLE IF NOT EXISTS projects (
  id SERIAL PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  client_name VARCHAR(100),
  address VARCHAR(300),
  area FLOAT,
  style VARCHAR(50),
  budget VARCHAR(50),
  status VARCHAR(30) DEFAULT '接洽中',
  description TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 项目文件表
CREATE TABLE IF NOT EXISTS project_files (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  filename VARCHAR(300),
  filepath VARCHAR(500),
  file_type VARCHAR(30),
  stage VARCHAR(30),
  uploaded_at TIMESTAMP DEFAULT NOW()
);

-- 项目笔记表
CREATE TABLE IF NOT EXISTS project_notes (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  note_type VARCHAR(30) DEFAULT '沟通记录',
  created_at TIMESTAMP DEFAULT NOW()
);

-- 客户表
CREATE TABLE IF NOT EXISTS clients (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  phone VARCHAR(30),
  wechat VARCHAR(100),
  source VARCHAR(100),
  budget_range VARCHAR(50),
  preferred_style VARCHAR(100),
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 灵感表
CREATE TABLE IF NOT EXISTS inspirations (
  id SERIAL PRIMARY KEY,
  title VARCHAR(200),
  description TEXT,
  image_path VARCHAR(500),
  source_url VARCHAR(500),
  tags JSONB,
  category VARCHAR(50),
  project_id INTEGER REFERENCES projects(id),
  created_at TIMESTAMP DEFAULT NOW()
);

-- AI 生成记录表
CREATE TABLE IF NOT EXISTS ai_generations (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id),
  prompt TEXT NOT NULL,
  negative_prompt TEXT,
  style VARCHAR(50),
  mode VARCHAR(20),
  input_image VARCHAR(500),
  output_image VARCHAR(500),
  model VARCHAR(100),
  parameters JSONB,
  status VARCHAR(20) DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Agent 配置表
CREATE TABLE IF NOT EXISTS agent_configs (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  display_name VARCHAR(100),
  role VARCHAR(50),
  system_prompt TEXT,
  capabilities JSONB,
  red_lines JSONB,
  autonomy_level VARCHAR(20) DEFAULT '执行',
  status VARCHAR(20) DEFAULT 'active',
  created_at TIMESTAMP DEFAULT NOW()
);

-- 材料表
CREATE TABLE IF NOT EXISTS materials (
  id SERIAL PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  category VARCHAR(50),
  brand VARCHAR(100),
  model VARCHAR(100),
  spec VARCHAR(200),
  unit VARCHAR(20),
  price FLOAT,
  color VARCHAR(50),
  texture VARCHAR(100),
  image_path VARCHAR(500),
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 用户表
CREATE TABLE IF NOT EXISTS users (
  id SERIAL PRIMARY KEY,
  phone VARCHAR(20) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(100),
  created_at TIMESTAMP DEFAULT NOW(),
  last_login TIMESTAMP
);

-- 创建索引
CREATE INDEX IF NOT EXISTS idx_projects_status ON projects(status);
CREATE INDEX IF NOT EXISTS idx_projects_client ON projects(client_name);
CREATE INDEX IF NOT EXISTS idx_clients_phone ON clients(phone);
CREATE INDEX IF NOT EXISTS idx_materials_category ON materials(category);
CREATE INDEX IF NOT EXISTS idx_inspirations_category ON inspirations(category);
"""

print("正在通过 Supabase REST API 创建表...")

# 尝试使用 Supabase 的 SQL API
headers = {
    "apikey": SUPABASE_KEY,
    "Authorization": f"Bearer {SUPABASE_KEY}",
    "Content-Type": "application/json",
    "Prefer": "resolution=merge-duplicates"
}

# 使用 Supabase 的 rpc 功能
try:
    # 尝试调用 exec_sql 函数
    response = requests.post(
        f"{SUPABASE_URL}/rest/v1/rpc/exec_sql",
        headers=headers,
        json={"query": SQL},
        timeout=30
    )
    
    if response.status_code == 200:
        print("✅ 表创建成功！")
    else:
        print(f"❌ 错误: {response.status_code}")
        print(response.text)
        
except Exception as e:
    print(f"❌ 请求失败: {e}")
    print("\n请手动在 Supabase SQL Editor 中执行 SQL。")
