"""材料库 API."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import get_db, Material
from pydantic import BaseModel
from typing import Optional

router = APIRouter()

class MaterialCreate(BaseModel):
    name: str
    category: Optional[str] = None
    brand: Optional[str] = None
    model: Optional[str] = None
    spec: Optional[str] = None
    unit: Optional[str] = None
    price: Optional[float] = None
    color: Optional[str] = None
    texture: Optional[str] = None
    notes: Optional[str] = None

@router.get("/")
def list_materials(category: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Material)
    if category:
        q = q.filter(Material.category == category)
    return [_m_to_dict(m) for m in q.order_by(Material.name).all()]

@router.post("/")
def create_material(data: MaterialCreate, db: Session = Depends(get_db)):
    m = Material(**data.model_dump())
    db.add(m)
    db.commit()
    db.refresh(m)
    return _m_to_dict(m)

@router.delete("/{mid}")
def delete_material(mid: int, db: Session = Depends(get_db)):
    m = db.query(Material).get(mid)
    if not m:
        raise HTTPException(404, "材料不存在")
    db.delete(m)
    db.commit()
    return {"ok": True}

def _m_to_dict(m):
    return {
        "id": m.id, "name": m.name, "category": m.category,
        "brand": m.brand, "model": m.model, "spec": m.spec,
        "unit": m.unit, "price": m.price, "color": m.color,
        "texture": m.texture, "notes": m.notes,
    }
