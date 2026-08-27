"""灵感库 API."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from models.database import get_db, Inspiration
from pydantic import BaseModel
from typing import Optional, List
import os, uuid, shutil, json

router = APIRouter()
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "inspiration")

class InspirationCreate(BaseModel):
    title: str
    description: Optional[str] = None
    source_url: Optional[str] = None
    tags: Optional[List[str]] = []
    category: Optional[str] = None
    project_id: Optional[int] = None

@router.get("/")
def list_inspirations(category: Optional[str] = None, tag: Optional[str] = None, project_id: Optional[int] = None, db: Session = Depends(get_db)):
    q = db.query(Inspiration)
    if category:
        q = q.filter(Inspiration.category == category)
    if project_id:
        q = q.filter(Inspiration.project_id == project_id)
    results = q.order_by(Inspiration.created_at.desc()).all()
    if tag:
        results = [i for i in results if i.tags and tag in i.tags]
    return [_i_to_dict(i) for i in results]

@router.post("/")
def create_inspiration(data: InspirationCreate, db: Session = Depends(get_db)):
    ins = Inspiration(**data.model_dump())
    db.add(ins)
    db.commit()
    db.refresh(ins)
    return _i_to_dict(ins)

@router.post("/upload")
async def upload_inspiration(file: UploadFile = File(...), title: str = Form(""), description: str = Form(""), tags: str = Form("[]"), category: str = Form(""), project_id: str = Form(""), db: Session = Depends(get_db)):
    ext = os.path.splitext(file.filename)[1]
    fname = f"{uuid.uuid4().hex}{ext}"
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    fpath = os.path.join(UPLOAD_DIR, fname)
    with open(fpath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    ins = Inspiration(
        title=title or file.filename,
        description=description,
        image_path=f"/uploads/inspiration/{fname}",
        tags=json.loads(tags) if tags else [],
        category=category or None,
        project_id=int(project_id) if project_id else None,
    )
    db.add(ins)
    db.commit()
    return _i_to_dict(ins)

@router.delete("/{iid}")
def delete_inspiration(iid: int, db: Session = Depends(get_db)):
    ins = db.query(Inspiration).get(iid)
    if not ins:
        raise HTTPException(404, "灵感不存在")
    db.delete(ins)
    db.commit()
    return {"ok": True}

def _i_to_dict(i):
    return {
        "id": i.id, "title": i.title, "description": i.description,
        "image_path": i.image_path, "source_url": i.source_url,
        "tags": i.tags or [], "category": i.category,
        "project_id": i.project_id, "created_at": str(i.created_at),
    }
