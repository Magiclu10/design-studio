"""Design Studio - FastAPI Main Application (云端版)。"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
import os

from models.database import init_db
from api import projects, inspirations, ai_generation, agents, materials, clients, online, auth
from services.auto_update import start_auto_update

app = FastAPI(title="路焉识设计工作室", version="1.0.0")

# CORS 配置（允许跨域请求）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 初始化数据库
@app.on_event("startup")
def startup():
    init_db()
    start_auto_update()

# 注册路由
app.include_router(auth.router, prefix="/api/auth", tags=["认证"])
app.include_router(projects.router, prefix="/api/projects", tags=["项目管理"])
app.include_router(inspirations.router, prefix="/api/inspirations", tags=["灵感库"])
app.include_router(ai_generation.router, prefix="/api/ai", tags=["AI生图"])
app.include_router(agents.router, prefix="/api/agents", tags=["Agent"])
app.include_router(materials.router, prefix="/api/materials", tags=["材料库"])
app.include_router(clients.router, prefix="/api/clients", tags=["客户管理"])
app.include_router(online.router, prefix="/api/online", tags=["在线资源"])

# 静态文件
FRONTEND = os.path.join(os.path.dirname(os.path.dirname(__file__)), "frontend")
app.mount("/static", StaticFiles(directory=FRONTEND), name="static")

# 上传文件
DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
os.makedirs(os.path.join(DATA_DIR, "uploads"), exist_ok=True)
app.mount("/uploads", StaticFiles(directory=os.path.join(DATA_DIR, "uploads")), name="uploads")

# 路由处理
@app.get("/")
async def root():
    return FileResponse(os.path.join(FRONTEND, "index.html"))

@app.get("/login.html")
async def login_page():
    return FileResponse(os.path.join(FRONTEND, "login.html"))

@app.get("/register.html")
async def register_page():
    return FileResponse(os.path.join(FRONTEND, "register.html"))

@app.get("/health")
async def health():
    return {"status": "ok", "name": "路焉识设计工作室", "version": "1.0.0"}

# PWA 支持
@app.get("/manifest.json")
async def manifest():
    return FileResponse(os.path.join(FRONTEND, "manifest.json"))

@app.get("/sw.js")
async def service_worker():
    return FileResponse(os.path.join(FRONTEND, "sw.js"))
