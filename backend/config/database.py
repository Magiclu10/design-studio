"""数据库配置 - 使用 Supabase PostgreSQL。"""
import os
from urllib.parse import quote_plus

# Supabase PostgreSQL 配置
SUPABASE_PASSWORD = quote_plus("zmz890327@123")
SUPABASE_HOST = "db.kntzsbpfsbcvbyqttksb.supabase.co"
SUPABASE_PORT = "5432"
SUPABASE_DB = "postgres"
SUPABASE_USER = "postgres"

# 构建数据库 URL
DATABASE_URL = f"postgresql://{SUPABASE_USER}:{SUPABASE_PASSWORD}@{SUPABASE_HOST}:{SUPABASE_PORT}/{SUPABASE_DB}"

# 设置代理环境变量
os.environ['HTTP_PROXY'] = 'http://127.0.0.1:17891'
os.environ['HTTPS_PROXY'] = 'http://127.0.0.1:17891'

def get_database_url():
    """获取数据库连接 URL。"""
    return DATABASE_URL
