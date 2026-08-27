"""创建测试用户。"""
import sys
import os

# 添加 backend 目录到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

from models.database import init_db, SessionLocal, User
from api.auth import hash_password

def create_test_user():
    """创建测试用户。"""
    init_db()
    db = SessionLocal()
    
    # 检查用户是否已存在
    existing = db.query(User).filter(User.phone == "13800138000").first()
    if existing:
        print("✅ 测试用户已存在")
        print(f"   手机号: {existing.phone}")
        print(f"   姓名: {existing.name}")
        db.close()
        return
    
    # 创建测试用户
    user = User(
        phone="13800138000",
        password_hash=hash_password("123456"),
        name="路焉识"
    )
    db.add(user)
    db.commit()
    
    print("✅ 测试用户创建成功！")
    print(f"   手机号: 13800138000")
    print(f"   密码: 123456")
    print(f"   姓名: 路焉识")
    
    db.close()

if __name__ == "__main__":
    create_test_user()
