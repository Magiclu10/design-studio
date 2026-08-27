"""用户认证 API。"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models.database import get_db, User
from pydantic import BaseModel
from typing import Optional
from datetime import datetime
import hashlib
import secrets

router = APIRouter()

class UserRegister(BaseModel):
    phone: str
    password: str
    name: Optional[str] = None

class UserLogin(BaseModel):
    phone: str
    password: str

class UserResponse(BaseModel):
    id: int
    phone: str
    name: Optional[str]
    created_at: str

def hash_password(password: str) -> str:
    """密码哈希。"""
    salt = secrets.token_hex(16)
    hash_obj = hashlib.sha256((password + salt).encode())
    return f"{salt}:{hash_obj.hexdigest()}"

def verify_password(password: str, hashed: str) -> bool:
    """验证密码。"""
    try:
        salt, hash_val = hashed.split(":")
        hash_obj = hashlib.sha256((password + salt).encode())
        return hash_obj.hexdigest() == hash_val
    except:
        return False

@router.post("/register", response_model=UserResponse)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    """用户注册。"""
    # 检查手机号是否已注册
    existing = db.query(User).filter(User.phone == user_data.phone).first()
    if existing:
        raise HTTPException(status_code=400, detail="该手机号已注册")
    
    # 创建用户
    user = User(
        phone=user_data.phone,
        password_hash=hash_password(user_data.password),
        name=user_data.name
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return UserResponse(
        id=user.id,
        phone=user.phone,
        name=user.name,
        created_at=str(user.created_at)
    )

@router.post("/login")
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    """用户登录。"""
    user = db.query(User).filter(User.phone == user_data.phone).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=401, detail="手机号或密码错误")
    
    # 更新最后登录时间
    user.last_login = datetime.now()
    db.commit()
    
    # 生成简单 token（生产环境应使用 JWT）
    token = secrets.token_hex(32)
    
    return {
        "token": token,
        "user": {
            "id": user.id,
            "phone": user.phone,
            "name": user.name
        }
    }

@router.get("/me")
def get_current_user(token: str, db: Session = Depends(get_db)):
    """获取当前用户信息（简化版，生产环境应验证 JWT）。"""
    # 这里简化处理，实际应该验证 token
    return {"message": "请使用 token 验证"}
