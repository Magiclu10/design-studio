"""通过代理连接 Supabase PostgreSQL。"""
import psycopg2
from urllib.parse import quote_plus
import os

# 设置代理
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:17891'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:17891'

# Supabase 数据库连接信息
password = quote_plus("zmz890327@123")
host = "db.kntzsbpfsbcvbyqttksb.supabase.co"
port = "5432"
database = "postgres"
user = "postgres"

# 构建连接字符串
conn_string = f"postgresql://{user}:{password}@{host}:{port}/{database}"

print("正在通过代理连接 Supabase 数据库...")

try:
    # 连接数据库
    conn = psycopg2.connect(conn_string)
    cursor = conn.cursor()
    
    print("✅ 连接成功！正在创建表...")
    
    # SQL 语句
    sql = """
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
    
    # 执行 SQL
    cursor.execute(sql)
    conn.commit()
    
    print("✅ 所有表创建成功！")
    
    # 验证表是否创建成功
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """)
    
    tables = cursor.fetchall()
    print(f"\n已创建 {len(tables)} 个表：")
    for table in tables:
        print(f"  - {table[0]}")
    
    cursor.close()
    conn.close()
    
    print("\n✅ 数据库初始化完成！")
    
except Exception as e:
    print(f"❌ 错误: {e}")
