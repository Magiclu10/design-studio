"""Supabase 配置和客户端。"""
import os
from supabase import create_client, Client

# Supabase 配置
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://kntzsbpfsbcvbyqttksb.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtudHpzYnBmc2JjdmJ5cXR0a3NiIiwicm9sZSI6ImFub24iLCJpYXQiOjE3ODc4MTQwNzgsImV4cCI6MjEwMzM5MDA3OH0.WHX89yefpdr9iqJ87B8Y9Cnl-sg2SPvnW4uQi8n1hkU")

# 创建 Supabase 客户端
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

def get_supabase() -> Client:
    """获取 Supabase 客户端实例。"""
    return supabase
