"""AI 生图 API — 框架预留，后续接入 NanoBanana / Google."""
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from models.database import get_db, AIGeneration
from pydantic import BaseModel
from typing import Optional, List
import os, uuid, shutil

router = APIRouter()

class GenerateRequest(BaseModel):
    prompt: str
    negative_prompt: Optional[str] = None
    style: Optional[str] = None
    mode: str = "txt2img"  # txt2img / img2img / style_transfer / inpaint
    project_id: Optional[int] = None
    width: Optional[int] = 1024
    height: Optional[int] = 1024
    model: Optional[str] = "nanobanana"

@router.post("/generate")
async def generate_image(data: GenerateRequest, db: Session = Depends(get_db)):
    """生成图片 — 目前返回占位，后续接入真实 API。"""
    gen = AIGeneration(
        project_id=data.project_id,
        prompt=data.prompt,
        negative_prompt=data.negative_prompt,
        style=data.style,
        mode=data.mode,
        model=data.model,
        parameters={"width": data.width, "height": data.height},
        status="pending",
    )
    db.add(gen)
    db.commit()
    db.refresh(gen)
    # TODO: 接入 NanoBanana API 调用
    # 目前返回占位信息
    return {
        "id": gen.id,
        "status": "pending",
        "message": "AI 生图接口已就绪，等待接入 NanoBanana API。请在设置中配置 API Key。",
        "prompt": gen.prompt,
    }

@router.get("/history")
def generation_history(project_id: Optional[int] = None, limit: int = 20, db: Session = Depends(get_db)):
    q = db.query(AIGeneration)
    if project_id:
        q = q.filter(AIGeneration.project_id == project_id)
    gens = q.order_by(AIGeneration.created_at.desc()).limit(limit).all()
    return [{
        "id": g.id, "prompt": g.prompt, "style": g.style,
        "mode": g.mode, "model": g.model, "status": g.status,
        "output_image": g.output_image, "created_at": str(g.created_at),
    } for g in gens]

@router.get("/styles")
def list_styles():
    """预设室内设计风格列表。"""
    return [
        {"id": "modern", "name": "现代简约", "prompt_hint": "modern minimalist interior"},
        {"id": "scandinavian", "name": "北欧风", "prompt_hint": "scandinavian style interior"},
        {"id": "japandi", "name": "侘寂/Japandi", "prompt_hint": "japandi wabi-sabi interior"},
        {"id": "chinese", "name": "新中式", "prompt_hint": "modern Chinese style interior"},
        {"id": "industrial", "name": "工业风", "prompt_hint": "industrial loft interior"},
        {"id": "french", "name": "法式", "prompt_hint": "French elegant interior"},
        {"id": "mediterranean", "name": "地中海", "prompt_hint": "Mediterranean style interior"},
        {"id": "artdeco", "name": "Art Deco", "prompt_hint": "art deco luxury interior"},
        {"id": "midcentury", "name": "中古风", "prompt_hint": "mid-century modern interior"},
        {"id": "minimalist", "name": "极简", "prompt_hint": "ultra minimalist interior"},
    ]
