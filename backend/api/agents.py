"""Agent 集成层 API."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import get_db, AgentConfig
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()

class AgentCreate(BaseModel):
    name: str
    display_name: str
    role: str
    system_prompt: str
    capabilities: Optional[List[str]] = []
    red_lines: Optional[List[str]] = []
    autonomy_level: Optional[str] = "执行"

class AgentUpdate(BaseModel):
    display_name: Optional[str] = None
    system_prompt: Optional[str] = None
    capabilities: Optional[List[str]] = None
    red_lines: Optional[List[str]] = None
    autonomy_level: Optional[str] = None
    status: Optional[str] = None

@router.get("/")
def list_agents(db: Session = Depends(get_db)):
    agents = db.query(AgentConfig).all()
    return [_a_to_dict(a) for a in agents]

@router.post("/")
def create_agent(data: AgentCreate, db: Session = Depends(get_db)):
    a = AgentConfig(**data.model_dump())
    db.add(a)
    db.commit()
    db.refresh(a)
    return _a_to_dict(a)

@router.get("/{aid}")
def get_agent(aid: int, db: Session = Depends(get_db)):
    a = db.query(AgentConfig).get(aid)
    if not a:
        raise HTTPException(404, "Agent不存在")
    return _a_to_dict(a)

@router.put("/{aid}")
def update_agent(aid: int, data: AgentUpdate, db: Session = Depends(get_db)):
    a = db.query(AgentConfig).get(aid)
    if not a:
        raise HTTPException(404, "Agent不存在")
    for k, v in data.model_dump(exclude_none=True).items():
        setattr(a, k, v)
    db.commit()
    return _a_to_dict(a)

@router.delete("/{aid}")
def delete_agent(aid: int, db: Session = Depends(get_db)):
    a = db.query(AgentConfig).get(aid)
    if not a:
        raise HTTPException(404, "Agent不存在")
    db.delete(a)
    db.commit()
    return {"ok": True}

def _a_to_dict(a):
    return {
        "id": a.id, "name": a.name, "display_name": a.display_name,
        "role": a.role, "system_prompt": a.system_prompt,
        "capabilities": a.capabilities or [], "red_lines": a.red_lines or [],
        "autonomy_level": a.autonomy_level, "status": a.status,
        "created_at": str(a.created_at),
    }
