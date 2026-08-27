"""客户管理 API."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import get_db, Client
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class ClientCreate(BaseModel):
    name: str
    phone: Optional[str] = None
    wechat: Optional[str] = None
    source: Optional[str] = None
    budget_range: Optional[str] = None
    preferred_style: Optional[str] = None
    notes: Optional[str] = None

class ClientUpdate(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    wechat: Optional[str] = None
    source: Optional[str] = None
    budget_range: Optional[str] = None
    preferred_style: Optional[str] = None
    notes: Optional[str] = None

@router.get("/")
def list_clients(db: Session = Depends(get_db)):
    clients = db.query(Client).order_by(Client.created_at.desc()).all()
    return [_c_to_dict(c) for c in clients]

@router.post("/")
def create_client(data: ClientCreate, db: Session = Depends(get_db)):
    c = Client(**data.model_dump())
    db.add(c)
    db.commit()
    db.refresh(c)
    return _c_to_dict(c)

@router.put("/{cid}")
def update_client(cid: int, data: ClientUpdate, db: Session = Depends(get_db)):
    c = db.query(Client).get(cid)
    if not c:
        raise HTTPException(404, "客户不存在")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(c, k, v)
    db.commit()
    return _c_to_dict(c)

@router.delete("/{cid}")
def delete_client(cid: int, db: Session = Depends(get_db)):
    c = db.query(Client).get(cid)
    if not c:
        raise HTTPException(404, "客户不存在")
    db.delete(c)
    db.commit()
    return {"ok": True}

def _c_to_dict(c):
    return {
        "id": c.id, "name": c.name, "phone": c.phone,
        "wechat": c.wechat, "source": c.source,
        "budget_range": c.budget_range, "preferred_style": c.preferred_style,
        "notes": c.notes, "created_at": str(c.created_at),
    }
