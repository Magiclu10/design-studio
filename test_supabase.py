"""测试 Supabase 连接。"""
import os
import sys

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from config.supabase import get_supabase

def test_connection():
    """测试 Supabase 连接。"""
    try:
        supabase = get_supabase()
        
        # 测试查询（先创建表如果不存在）
        print("✅ Supabase 客户端创建成功！")
        print(f"   URL: {supabase.supabase_url}")
        
        # 尝试查询 projects 表
        try:
            result = supabase.table('projects').select('*').limit(1).execute()
            print(f"   查询测试: 返回 {len(result.data)} 条记录")
        except Exception as e:
            print(f"   查询测试: 表可能不存在（需要先创建表）")
            print(f"   错误信息: {e}")
        
        return True
    except Exception as e:
        print(f"❌ Supabase 连接失败: {e}")
        return False

if __name__ == "__main__":
    test_connection()
