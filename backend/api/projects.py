"""项目管理 API."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from models.database import get_db, Project, ProjectFile, ProjectNote
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
import os, shutil, uuid

router = APIRouter()
UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data", "uploads")

class ProjectCreate(BaseModel):
    name: str
    client_name: Optional[str] = None
    address: Optional[str] = None
    area: Optional[float] = None
    style: Optional[str] = None
    budget: Optional[str] = None
    description: Optional[str] = None

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    client_name: Optional[str] = None
    address: Optional[str] = None
    area: Optional[float] = None
    style: Optional[str] = None
    budget: Optional[str] = None
    status: Optional[str] = None
    description: Optional[str] = None

class NoteCreate(BaseModel):
    content: str
    note_type: Optional[str] = "沟通记录"

@router.get("/")
def list_projects(status: Optional[str] = None, db: Session = Depends(get_db)):
    q = db.query(Project)
    if status:
        q = q.filter(Project.status == status)
    return [p_to_dict(p) for p in q.order_by(Project.updated_at.desc()).all()]

@router.post("/")
def create_project(data: ProjectCreate, db: Session = Depends(get_db)):
    p = Project(**data.model_dump())
    db.add(p)
    db.commit()
    db.refresh(p)
    return p_to_dict(p)

@router.get("/{pid}")
def get_project(pid: int, db: Session = Depends(get_db)):
    p = db.query(Project).get(pid)
    if not p:
        raise HTTPException(404, "项目不存在")
    return p_to_dict(p, detail=True)

@router.put("/{pid}")
def update_project(pid: int, data: ProjectUpdate, db: Session = Depends(get_db)):
    p = db.query(Project).get(pid)
    if not p:
        raise HTTPException(404, "项目不存在")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(p, k, v)
    p.updated_at = datetime.now()
    db.commit()
    return p_to_dict(p)

@router.delete("/{pid}")
def delete_project(pid: int, db: Session = Depends(get_db)):
    p = db.query(Project).get(pid)
    if not p:
        raise HTTPException(404, "项目不存在")
    db.delete(p)
    db.commit()
    return {"ok": True}

@router.post("/{pid}/files")
async def upload_file(pid: int, file: UploadFile = File(...), file_type: str = Form("其他"), stage: str = Form(""), db: Session = Depends(get_db)):
    p = db.query(Project).get(pid)
    if not p:
        raise HTTPException(404, "项目不存在")
    ext = os.path.splitext(file.filename)[1]
    fname = f"{uuid.uuid4().hex}{ext}"
    fpath = os.path.join(UPLOAD_DIR, fname)
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    with open(fpath, "wb") as f:
        shutil.copyfileobj(file.file, f)
    pf = ProjectFile(project_id=pid, filename=file.filename, filepath=f"/uploads/{fname}", file_type=file_type, stage=stage)
    db.add(pf)
    db.commit()
    return {"id": pf.id, "filename": pf.filename, "filepath": pf.filepath}

@router.get("/{pid}/files")
def list_files(pid: int, db: Session = Depends(get_db)):
    files = db.query(ProjectFile).filter(ProjectFile.project_id == pid).all()
    return [{"id": f.id, "filename": f.filename, "filepath": f.filepath, "file_type": f.file_type, "stage": f.stage} for f in files]

@router.post("/{pid}/notes")
def add_note(pid: int, data: NoteCreate, db: Session = Depends(get_db)):
    n = ProjectNote(project_id=pid, content=data.content, note_type=data.note_type)
    db.add(n)
    db.commit()
    return {"id": n.id, "content": n.content, "note_type": n.note_type, "created_at": str(n.created_at)}

@router.get("/{pid}/notes")
def list_notes(pid: int, db: Session = Depends(get_db)):
    notes = db.query(ProjectNote).filter(ProjectNote.project_id == pid).order_by(ProjectNote.created_at.desc()).all()
    return [{"id": n.id, "content": n.content, "note_type": n.note_type, "created_at": str(n.created_at)} for n in notes]

def p_to_dict(p, detail=False):
    d = {
        "id": p.id, "name": p.name, "client_name": p.client_name,
        "address": p.address, "area": p.area, "style": p.style,
        "budget": p.budget, "status": p.status, "description": p.description,
        "created_at": str(p.created_at), "updated_at": str(p.updated_at),
        "file_count": len(p.files) if p.files else 0,
    }
    if detail:
        d["files"] = [{"id": f.id, "filename": f.filename, "filepath": f.filepath, "file_type": f.file_type, "stage": f.stage} for f in (p.files or [])]
        d["notes"] = [{"id": n.id, "content": n.content, "note_type": n.note_type, "created_at": str(n.created_at)} for n in (p.notes or [])]
    return d
