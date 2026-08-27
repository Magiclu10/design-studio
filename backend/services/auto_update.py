"""定时更新服务 — 自动从设计网站抓取新内容。"""
import threading
import time
import urllib.request
import json
import ssl
import re
import os
from datetime import datetime

ssl._create_default_https_context = ssl._create_unverified_context

# 更新日志
UPDATE_LOG = []

# 图片关键词映射（用于搜索设计图片）
DESIGN_QUERIES = [
    "modern living room interior design",
    "scandinavian bedroom design",
    "minimalist kitchen design",
    "japanese wabi-sabi interior",
    "industrial loft design",
    "french luxury interior",
    "chinese traditional modern",
    "nursery room design",
    "walk-in closet design",
    "bathroom marble design",
    "wood texture floor",
    "ceramic tile pattern",
    "wall paint color",
    "lighting fixture design",
    "furniture modern design",
]


def fetch_unsplash_images(query: str, count: int = 3) -> list:
    """从 Unsplash 获取设计图片 URL。"""
    try:
        url = f"https://unsplash.com/napi/search/photos?query={query}&per_page={count}"
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json",
        })
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            results = data.get("results", [])
            return [{
                "url": r["urls"]["regular"],
                "description": r.get("description") or r.get("alt_description") or query,
                "author": r["user"]["name"],
                "source": "Unsplash",
            } for r in results if r.get("urls")]
    except Exception as e:
        return []


def fetch_design_content() -> dict:
    """抓取设计内容，返回灵感和材料数据。"""
    inspirations = []
    materials = []

    # 使用 Unsplash Source API（更稳定）
    design_topics = [
        {"query": "modern+living+room", "title": "现代简约客厅", "tags": ["现代", "客厅", "简约"]},
        {"query": "scandinavian+bedroom", "title": "北欧风卧室", "tags": ["北欧", "卧室", "温馨"]},
        {"query": "minimalist+kitchen", "title": "极简厨房设计", "tags": ["极简", "厨房", "白色"]},
        {"query": "japanese+interior", "title": "日式侘寂空间", "tags": ["日式", "侘寂", "原木"]},
        {"query": "industrial+loft", "title": "工业风 Loft", "tags": ["工业风", "loft", "个性"]},
        {"query": "luxury+bathroom", "title": "奢华卫生间", "tags": ["奢华", "卫生间", "大理石"]},
        {"query": "chinese+style", "title": "新中式空间", "tags": ["新中式", "传统", "现代"]},
        {"query": "bohemian+room", "title": "波西米亚风格", "tags": ["波西米亚", "混搭", "色彩"]},
    ]

    import random
    topic = random.choice(design_topics)

    # 生成 Unsplash Source URL（无需 API Key）
    for i in range(5):
        width = random.randint(600, 800)
        height = random.randint(400, 600)
        image_url = f"https://source.unsplash.com/random/{width}x{height}/?{topic['query']}&sig={random.randint(1,10000)}"

        inspirations.append({
            "title": f"{topic['title']} #{i+1}",
            "description": f"来自 Unsplash 的 {topic['title']} 设计灵感",
            "image_url": image_url,
            "tags": topic["tags"] + [f"方案{i+1}"],
            "category": "风格",
            "source": "Unsplash",
        })

    return {"inspirations": inspirations, "materials": materials}


def auto_update_task():
    """后台定时更新任务。"""
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

    while True:
        try:
            # 每 30 分钟更新一次
            time.sleep(1800)

            result = fetch_design_content()

            if result["inspirations"]:
                # 保存到文件
                data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
                cache_file = os.path.join(data_dir, "online_cache.json")

                # 读取现有缓存
                existing = {"inspirations": [], "last_update": None}
                if os.path.exists(cache_file):
                    with open(cache_file, "r", encoding="utf-8") as f:
                        existing = json.load(f)

                # 合并新数据（去重）
                existing_titles = {i["title"] for i in existing["inspirations"]}
                new_inspirations = [i for i in result["inspirations"] if i["title"] not in existing_titles]

                if new_inspirations:
                    existing["inspirations"] = new_inspirations + existing["inspirations"]
                    # 保留最近 100 条
                    existing["inspirations"] = existing["inspirations"][:100]
                    existing["last_update"] = datetime.now().isoformat()

                    with open(cache_file, "w", encoding="utf-8") as f:
                        json.dump(existing, f, ensure_ascii=False, indent=2)

                    UPDATE_LOG.append({
                        "time": datetime.now().isoformat(),
                        "added": len(new_inspirations),
                        "total": len(existing["inspirations"]),
                    })

                    print(f"[自动更新] 新增 {len(new_inspirations)} 条灵感，总计 {len(existing['inspirations'])} 条")

        except Exception as e:
            print(f"[自动更新错误] {e}")


def start_auto_update():
    """启动自动更新线程。"""
    thread = threading.Thread(target=auto_update_task, daemon=True)
    thread.start()
    print("[自动更新] 已启动，每 30 分钟检查一次新内容")
    return thread


def get_update_log() -> list:
    """获取更新日志。"""
    return UPDATE_LOG[-20:]  # 返回最近 20 条


def get_cached_content() -> dict:
    """获取缓存的在线内容。"""
    # 路径：backend/services/auto_update.py -> backend -> project_root -> data
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "data")
    cache_file = os.path.join(data_dir, "online_cache.json")
    
    print(f"[DEBUG] Cache file path: {cache_file}")
    print(f"[DEBUG] File exists: {os.path.exists(cache_file)}")

    if os.path.exists(cache_file):
        with open(cache_file, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"inspirations": [], "last_update": None}
