"""在线灵感导入 API — 从设计网站获取灵感素材。"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from models.database import get_db, Inspiration
import urllib.request
import json
import re
import ssl
from typing import Optional

router = APIRouter()

# 忽略 SSL 验证（某些网站证书问题）
ssl._create_default_https_context = ssl._create_unverified_context

# 设计网站数据源配置
DESIGN_SOURCES = {
    "zhisheji": {
        "name": "知末",
        "url": "https://www.zhisheji.com",
        "type": "inspiration",
    },
    "jia": {
        "name": "齐家网",
        "url": "https://www.jia.com",
        "type": "materials",
    },
    "to8to": {
        "name": "土巴兔",
        "url": "https://www.to8to.com",
        "type": "both",
    },
    "unsplash": {
        "name": "Unsplash",
        "url": "https://unsplash.com",
        "type": "inspiration",
    },
}

# 预设室内设计灵感数据（精选）
CURATED_INSPIRATIONS = [
    {
        "title": "现代简约客厅 · 白+木",
        "description": "白色墙面搭配浅木色家具，大面积落地窗引入自然光，灰色布艺沙发作为过渡色",
        "category": "风格",
        "tags": ["现代简约", "客厅", "木色", "自然光"],
        "source": "知末",
        "image_url": "https://images.unsplash.com/photo-1586023492125-27b2c045efd7?w=600",
    },
    {
        "title": "侘寂风卧室 · 水泥质感",
        "description": "微水泥墙面+亚麻床品+原木床头柜，低饱和度配色营造静谧氛围",
        "category": "风格",
        "tags": ["侘寂", "卧室", "微水泥", "低饱和"],
        "source": "知末",
        "image_url": "https://images.unsplash.com/photo-1616594039964-ae9021a400a0?w=600",
    },
    {
        "title": "新中式书房 · 实木书架",
        "description": "深色实木书架+宣纸灯+水墨画，传统元素与现代功能结合",
        "category": "空间",
        "tags": ["新中式", "书房", "实木", "水墨"],
        "source": "知末",
        "image_url": "https://images.unsplash.com/photo-1524758631624-e2822e304c36?w=600",
    },
    {
        "title": "北欧风厨房 · 白色小砖",
        "description": "白色地铁砖+浅灰橱柜+黄铜把手，清新明亮的北欧厨房",
        "category": "空间",
        "tags": ["北欧", "厨房", "白色砖", "黄铜"],
        "source": "齐家网",
        "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=600",
    },
    {
        "title": "法式轻奢卫生间 · 大理石",
        "description": "白色大理石墙面+金色五金件+独立浴缸，优雅复古的法式浴室",
        "category": "空间",
        "tags": ["法式", "卫生间", "大理石", "金色"],
        "source": "知末",
        "image_url": "https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?w=600",
    },
    {
        "title": "工业风loft · 裸露红砖",
        "description": "裸露红砖墙+铁艺书架+皮质沙发，粗犷个性的工业风空间",
        "category": "风格",
        "tags": ["工业风", "loft", "红砖", "铁艺"],
        "source": "土巴兔",
        "image_url": "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=600",
    },
    {
        "title": "日式原木玄关 · 鞋柜设计",
        "description": "浅木色鞋柜+换鞋凳+挂钩区，功能齐全的玄关收纳系统",
        "category": "空间",
        "tags": ["日式", "玄关", "原木", "收纳"],
        "source": "齐家网",
        "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=600",
    },
    {
        "title": "莫兰迪色系儿童房",
        "description": "低饱和度莫兰迪配色+圆角家具+充足收纳，温柔又安全的儿童空间",
        "category": "空间",
        "tags": ["莫兰迪", "儿童房", "低饱和", "安全"],
        "source": "知末",
        "image_url": "https://images.unsplash.com/photo-1519710164239-da123dc03ef4?w=600",
    },
    {
        "title": "极简衣帽间 · 玻璃门",
        "description": "长虹玻璃门+感应灯带+分区收纳，通透又整洁的衣帽间",
        "category": "空间",
        "tags": ["极简", "衣帽间", "玻璃", "灯带"],
        "source": "土巴兔",
        "image_url": "https://images.unsplash.com/photo-1558997519-83ea9252edf8?w=600",
    },
    {
        "title": "奶油风阳台 · 拱形门洞",
        "description": "拱形门洞+奶油色墙面+藤编家具，打造温馨休闲角落",
        "category": "风格",
        "tags": ["奶油风", "阳台", "拱形", "藤编"],
        "source": "知末",
        "image_url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=600",
    },
    {
        "title": "深色系主卧 · 墨绿墙",
        "description": "墨绿色背景墙+黄铜壁灯+丝绒床品，沉稳大气的复古主卧",
        "category": "风格",
        "tags": ["复古", "卧室", "墨绿", "丝绒"],
        "source": "知末",
        "image_url": "https://images.unsplash.com/photo-1616594039964-ae9021a400a0?w=600",
    },
    {
        "title": "开放式厨房 · 中岛设计",
        "description": "白色中岛台+吧台椅+吊灯组，集烹饪、用餐、社交于一体",
        "category": "空间",
        "tags": ["开放式", "厨房", "中岛", "吧台"],
        "source": "齐家网",
        "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=600",
    },
]

# 预设材料数据
CURATED_MATERIALS = [
    {"name": "大自然实木地板 · 橡木", "category": "地板", "brand": "大自然", "model": "橡木本色", "spec": "1210×165×15mm", "unit": "㎡", "price": 358, "color": "原木色", "image_url": "https://images.unsplash.com/photo-1600166898405-da9535204843?w=400"},
    {"name": "圣象强化地板 · 灰橡", "category": "地板", "brand": "圣象", "model": "N8028", "spec": "1212×195×11mm", "unit": "㎡", "price": 168, "color": "浅灰", "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=400"},
    {"name": "马可波罗瓷砖 · 大理石纹", "category": "瓷砖", "brand": "马可波罗", "model": "CH8013", "spec": "800×800mm", "unit": "㎡", "price": 289, "color": "白色", "image_url": "https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?w=400"},
    {"name": "东鹏瓷砖 · 水泥灰", "category": "瓷砖", "brand": "东鹏", "model": "YF806502", "spec": "800×800mm", "unit": "㎡", "price": 198, "color": "灰色", "image_url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=400"},
    {"name": "多乐士竹炭清新居 · 白色", "category": "墙漆", "brand": "多乐士", "model": "A991", "spec": "5L/桶", "unit": "桶", "price": 498, "color": "白色", "image_url": "https://images.unsplash.com/photo-1562259929-b4e1fd3aef09?w=400"},
    {"name": "立邦抗甲醛净味五合一", "category": "墙漆", "brand": "立邦", "model": "净味五合一", "spec": "5L/桶", "unit": "桶", "price": 428, "color": "白色", "image_url": "https://images.unsplash.com/photo-1589939705384-5185137a7f0f?w=400"},
    {"name": "兔宝宝生态板 · 橡木", "category": "木材", "brand": "兔宝宝", "model": "E0级", "spec": "1220×2440×18mm", "unit": "张", "price": 298, "color": "原木色", "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=400"},
    {"name": "莫干山细木工板", "category": "木材", "brand": "莫干山", "model": "E0级", "spec": "1220×2440×18mm", "unit": "张", "price": 258, "color": "本色", "image_url": "https://images.unsplash.com/photo-1600166898405-da9535204843?w=400"},
    {"name": "九牧花洒套装 · 恒温", "category": "五金", "brand": "九牧", "model": "36335", "spec": "恒温花洒", "unit": "套", "price": 1599, "color": "银色", "image_url": "https://images.unsplash.com/photo-1552321554-5fefe8c9ef14?w=400"},
    {"name": "科勒马桶 · 虹吸式", "category": "五金", "brand": "科勒", "model": "K-3856T", "spec": "连体马桶", "unit": "个", "price": 2899, "color": "白色", "image_url": "https://images.unsplash.com/photo-1584622650111-993a426fbf0a?w=400"},
    {"name": "欧普吸顶灯 · 客厅", "category": "灯具", "brand": "欧普", "model": "LED三色调光", "spec": "72W", "unit": "个", "price": 399, "color": "白色", "image_url": "https://images.unsplash.com/photo-1507473885765-e6ed057ab6fe?w=400"},
    {"name": "雷士射灯 · 嵌入式", "category": "灯具", "brand": "雷士", "model": "LED COB", "spec": "7W", "unit": "个", "price": 45, "color": "白色", "image_url": "https://images.unsplash.com/photo-1524484485831-a92ffc0de03f?w=400"},
    {"name": "杜邦可丽耐台面", "category": "石材", "brand": "杜邦", "model": "可丽耐", "spec": "定制", "unit": "延米", "price": 1800, "color": "白色", "image_url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?w=400"},
    {"name": "中迅石英石台面", "category": "石材", "brand": "中迅", "model": "ZXS-001", "spec": "15mm厚", "unit": "延米", "price": 680, "color": "灰色", "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=400"},
    {"name": "TATA木门 · 静音门", "category": "五金", "brand": "TATA", "model": "@001", "spec": "标准门", "unit": "樘", "price": 1899, "color": "白色", "image_url": "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=400"},
]


@router.get("/sources")
def list_sources():
    """列出可用的在线数据源。"""
    return [{"id": k, "name": v["name"], "url": v["url"], "type": v["type"]} for k, v in DESIGN_SOURCES.items()]


@router.get("/online/inspirations")
def get_online_inspirations(page: int = 1, limit: int = 12):
    """获取精选在线灵感（预设数据 + 自动更新缓存）。"""
    from services.auto_update import get_cached_content
    cache = get_cached_content()
    
    # 合并预设数据和缓存数据
    all_items = CURATED_INSPIRATIONS.copy()
    if cache.get("inspirations"):
        # 去重
        existing_titles = {i["title"] for i in all_items}
        for item in cache["inspirations"]:
            if item["title"] not in existing_titles:
                all_items.append(item)
                existing_titles.add(item["title"])
    
    start = (page - 1) * limit
    end = start + limit
    items = all_items[start:end]
    return {
        "items": items,
        "total": len(all_items),
        "page": page,
        "has_more": end < len(all_items),
        "last_update": cache.get("last_update"),
    }


@router.get("/online/materials")
def get_online_materials(category: Optional[str] = None, page: int = 1, limit: int = 15):
    """获取精选在线材料数据。"""
    items = CURATED_MATERIALS
    if category and category != "全部":
        items = [m for m in items if m["category"] == category]
    start = (page - 1) * limit
    end = start + limit
    return {
        "items": items[start:end],
        "total": len(items),
        "page": page,
        "has_more": end < len(items),
    }


@router.post("/import/inspiration/{index}")
def import_inspiration(index: int, db: Session = Depends(get_db)):
    """将在线灵感导入到本地灵感库。"""
    if index < 0 or index >= len(CURATED_INSPIRATIONS):
        raise HTTPException(404, "灵感不存在")
    item = CURATED_INSPIRATIONS[index]
    ins = Inspiration(
        title=item["title"],
        description=item["description"],
        image_path=item.get("image_url"),
        source_url=item.get("source_url", ""),
        tags=item.get("tags", []),
        category=item.get("category"),
    )
    db.add(ins)
    db.commit()
    return {"ok": True, "message": f"已导入：{item['title']}"}


@router.post("/import/material/{index}")
def import_material(index: int, db: Session = Depends(get_db)):
    """将在线材料导入到本地材料库。"""
    from models.database import Material
    if index < 0 or index >= len(CURATED_MATERIALS):
        raise HTTPException(404, "材料不存在")
    item = CURATED_MATERIALS[index]
    mat = Material(
        name=item["name"],
        category=item["category"],
        brand=item.get("brand"),
        model=item.get("model"),
        spec=item.get("spec"),
        unit=item.get("unit"),
        price=item.get("price"),
        color=item.get("color"),
    )
    db.add(mat)
    db.commit()
    return {"ok": True, "message": f"已导入：{item['name']}"}


@router.post("/import/inspirations/batch")
def batch_import_inspirations(indices: list[int], db: Session = Depends(get_db)):
    """批量导入在线灵感。"""
    imported = 0
    for idx in indices:
        if 0 <= idx < len(CURATED_INSPIRATIONS):
            item = CURATED_INSPIRATIONS[idx]
            ins = Inspiration(
                title=item["title"],
                description=item["description"],
                image_path=item.get("image_url"),
                tags=item.get("tags", []),
                category=item.get("category"),
            )
            db.add(ins)
            imported += 1
    db.commit()
    return {"ok": True, "imported": imported}


@router.get("/update/status")
def get_update_status():
    """获取自动更新状态。"""
    from services.auto_update import get_update_log, get_cached_content
    cache = get_cached_content()
    log = get_update_log()
    return {
        "last_update": cache.get("last_update"),
        "total_cached": len(cache.get("inspirations", [])),
        "recent_updates": log,
        "auto_update_enabled": True,
        "update_interval_minutes": 30,
    }

@router.post("/update/force")
def force_update():
    """强制触发一次更新。"""
    from services.auto_update import fetch_design_content
    import json
    import os
    from datetime import datetime
    
    result = fetch_design_content()
    
    # 保存到缓存文件
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    cache_file = os.path.join(data_dir, "online_cache.json")
    
    # 读取现有缓存
    existing = {"inspirations": [], "last_update": None}
    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            existing = json.load(f)
    
    # 合并新数据
    existing_titles = {i["title"] for i in existing["inspirations"]}
    new_inspirations = [i for i in result.get("inspirations", []) if i["title"] not in existing_titles]
    
    if new_inspirations:
        existing["inspirations"] = new_inspirations + existing["inspirations"]
        existing["inspirations"] = existing["inspirations"][:100]
        existing["last_update"] = datetime.now().isoformat()
        
        with open(cache_file, "w", encoding="utf-8") as f:
            json.dump(existing, f, ensure_ascii=False, indent=2)
    
    return {
        "ok": True,
        "new_inspirations": len(new_inspirations),
        "total_cached": len(existing["inspirations"]),
        "message": f"已获取 {len(new_inspirations)} 条新内容，总计 {len(existing['inspirations'])} 条",
    }

@router.post("/fetch-url")
def fetch_url_content(url: str):
    """从 URL 抓取内容（用于从任意设计网站导入）。"""
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        with urllib.request.urlopen(req, timeout=10) as resp:
            html = resp.read().decode("utf-8", errors="ignore")

        # 提取标题
        title_match = re.search(r"<title>(.*?)</title>", html, re.IGNORECASE | re.DOTALL)
        title = title_match.group(1).strip() if title_match else "未知标题"

        # 提取图片
        images = re.findall(r'<img[^>]+src=["\']([^"\']+)["\']', html)
        images = [img for img in images if not img.startswith("data:") and ("jpg" in img.lower() or "png" in img.lower() or "webp" in img.lower() or "jpeg" in img.lower())][:5]

        return {
            "title": title,
            "images": images,
            "url": url,
        }
    except Exception as e:
        raise HTTPException(400, f"抓取失败: {str(e)}")
