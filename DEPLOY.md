# 设计工作站 - 云端部署指南

## 一、Supabase 配置

### 1. 创建数据库表

登录 Supabase Dashboard → SQL Editor，执行以下 SQL：

```sql
-- 项目表
CREATE TABLE projects (
  id SERIAL PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  client_name VARCHAR(100),
  address VARCHAR(300),
  area FLOAT,
  style VARCHAR(50),
  budget VARCHAR(50),
  status VARCHAR(30) DEFAULT '接洽中',
  description TEXT,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

-- 项目文件表
CREATE TABLE project_files (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  filename VARCHAR(300),
  filepath VARCHAR(500),
  file_type VARCHAR(30),
  stage VARCHAR(30),
  uploaded_at TIMESTAMP DEFAULT NOW()
);

-- 项目笔记表
CREATE TABLE project_notes (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
  content TEXT NOT NULL,
  note_type VARCHAR(30) DEFAULT '沟通记录',
  created_at TIMESTAMP DEFAULT NOW()
);

-- 客户表
CREATE TABLE clients (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  phone VARCHAR(30),
  wechat VARCHAR(100),
  source VARCHAR(100),
  budget_range VARCHAR(50),
  preferred_style VARCHAR(100),
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 灵感表
CREATE TABLE inspirations (
  id SERIAL PRIMARY KEY,
  title VARCHAR(200),
  description TEXT,
  image_path VARCHAR(500),
  source_url VARCHAR(500),
  tags JSONB,
  category VARCHAR(50),
  project_id INTEGER REFERENCES projects(id),
  created_at TIMESTAMP DEFAULT NOW()
);

-- AI 生成记录表
CREATE TABLE ai_generations (
  id SERIAL PRIMARY KEY,
  project_id INTEGER REFERENCES projects(id),
  prompt TEXT NOT NULL,
  negative_prompt TEXT,
  style VARCHAR(50),
  mode VARCHAR(20),
  input_image VARCHAR(500),
  output_image VARCHAR(500),
  model VARCHAR(100),
  parameters JSONB,
  status VARCHAR(20) DEFAULT 'pending',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Agent 配置表
CREATE TABLE agent_configs (
  id SERIAL PRIMARY KEY,
  name VARCHAR(100) NOT NULL UNIQUE,
  display_name VARCHAR(100),
  role VARCHAR(50),
  system_prompt TEXT,
  capabilities JSONB,
  red_lines JSONB,
  autonomy_level VARCHAR(20) DEFAULT '执行',
  status VARCHAR(20) DEFAULT 'active',
  created_at TIMESTAMP DEFAULT NOW()
);

-- 材料表
CREATE TABLE materials (
  id SERIAL PRIMARY KEY,
  name VARCHAR(200) NOT NULL,
  category VARCHAR(50),
  brand VARCHAR(100),
  model VARCHAR(100),
  spec VARCHAR(200),
  unit VARCHAR(20),
  price FLOAT,
  color VARCHAR(50),
  texture VARCHAR(100),
  image_path VARCHAR(500),
  notes TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);

-- 用户表
CREATE TABLE users (
  id SERIAL PRIMARY KEY,
  phone VARCHAR(20) UNIQUE NOT NULL,
  password_hash VARCHAR(255) NOT NULL,
  name VARCHAR(100),
  created_at TIMESTAMP DEFAULT NOW(),
  last_login TIMESTAMP
);

-- 创建索引
CREATE INDEX idx_projects_status ON projects(status);
CREATE INDEX idx_projects_client ON projects(client_name);
CREATE INDEX idx_clients_phone ON clients(phone);
CREATE INDEX idx_materials_category ON materials(category);
CREATE INDEX idx_inspirations_category ON inspirations(category);
```

### 2. 获取连接信息

在 Supabase Dashboard → Settings → Database：
- **Host**: `db.kntzsbpfsbcvbyqttksb.supabase.co`
- **Database**: `postgres`
- **Port**: `5432`
- **User**: `postgres`
- **Password**: 你设置的密码

连接字符串：
```
postgresql://postgres:你的密码@db.kntzsbpfsbcvbyqttksb.supabase.co:5432/postgres
```

---

## 二、Railway 部署（后端）

### 1. 准备代码

```bash
# 进入项目目录
cd design-studio

# 创建 Procfile
echo "web: uvicorn backend.main:app --host 0.0.0.0 --port \$PORT" > Procfile
```

### 2. 部署到 Railway

1. 打开 [railway.app](https://railway.app)
2. 点击 "New Project" → "Deploy from GitHub repo"
3. 选择你的仓库
4. 添加环境变量：
   - `DATABASE_URL`: `postgresql://postgres:密码@db.kntzsbpfsbcvbyqttksb.supabase.co:5432/postgres`
   - `SUPABASE_URL`: `https://kntzsbpfsbcvbyqttksb.supabase.co`
   - `SUPABASE_KEY`: `eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
5. 点击 "Deploy"

### 3. 获取后端 URL

部署完成后，Railway 会给你一个 URL，类似：
```
https://design-studio-production.up.railway.app
```

---

## 三、Vercel 部署（前端）

### 1. 修改前端配置

编辑 `frontend/js/app.js`，修改 API 地址：

```javascript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8080';
```

### 2. 部署到 Vercel

1. 打开 [vercel.com](https://vercel.com)
2. 点击 "New Project"
3. 导入你的 GitHub 仓库
4. 配置：
   - **Framework Preset**: Other
   - **Root Directory**: `frontend`
   - **Build Command**: 留空
   - **Output Directory**: `.`
5. 添加环境变量：
   - `NEXT_PUBLIC_API_URL`: 你的 Railway 后端 URL
6. 点击 "Deploy"

### 3. 获取前端 URL

部署完成后，Vercel 会给你一个 URL，类似：
```
https://design-studio.vercel.app
```

---

## 四、手机端使用

### 1. 打开网站

在手机浏览器打开 Vercel 给你的 URL。

### 2. 添加到主屏幕

**iPhone (Safari)**:
1. 点击底部分享按钮（方框+箭头）
2. 选择 "添加到主屏幕"
3. 点击 "添加"

**Android (Chrome)**:
1. 点击右上角菜单（三个点）
2. 选择 "添加到主屏幕"
3. 点击 "添加"

### 3. 使用 App

现在你可以像使用原生 App 一样使用设计工作站了！

---

## 五、数据同步

- 电脑和手机访问同一个 URL，数据自动同步
- 所有数据存储在 Supabase 云端
- 支持多设备同时登录

---

## 六、常见问题

### Q: 部署失败怎么办？
A: 检查环境变量是否正确，特别是 `DATABASE_URL`。

### Q: 手机无法访问？
A: 确保后端 CORS 配置正确，允许跨域请求。

### Q: 数据丢失？
A: Supabase 免费版有 500MB 存储限制，定期备份重要数据。

### Q: 如何更新？
A: 推送代码到 GitHub，Railway 和 Vercel 会自动重新部署。

---

## 七、成本

| 服务 | 费用 |
|---|---|
| Supabase (数据库) | 免费 (500MB) |
| Railway (后端) | 免费 (500小时/月) |
| Vercel (前端) | 免费 |
| **总计** | **¥0/月** |

如果超出免费额度：
- Supabase Pro: $25/月
- Railway Pro: $5/月
- Vercel Pro: $20/月

---

## 八、安全建议

1. **修改默认密码**：部署后立即修改数据库密码
2. **启用 RLS**：在 Supabase 启用 Row Level Security
3. **使用 HTTPS**：Railway 和 Vercel 默认提供 HTTPS
4. **定期备份**：Supabase 免费版不自动备份，手动导出重要数据

---

## 九、联系方式

如有问题，请联系开发者。
