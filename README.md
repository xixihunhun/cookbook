# 🍳 夫妻点菜 · Cookbook

**淘宝闪购风格 · 微信小程序 · H5 · 多端运行**

夫妻两个人绑定家庭，每天一起抽签投票决定吃什么！

后端 Flask + SQLite，前端 Taro (Vue3 + TS)，支持微信小程序 / H5 / React Native。

---

## ✨ 核心玩法

```
老王 🤝 小红 → 绑定家庭 → 每天抽签投票 → 🏆 达成一致 → 就吃它了！
```

| 模块 | 功能 |
|------|------|
| 🔐 登录 | **微信授权登录**（真实 code2session），开发环境无 code 自动模拟 |
| 🏠 家庭 | 创建家庭 → 生成邀请码 → 伴侣输入邀请码加入（最多 2 人） |
| 🎲 抽签 | 每日推荐 8 个候选菜谱，两个人各投一票 |
| 📊 结果 | 同票 = 达成一致！不同 = 再投一次 |
| 🍳 菜谱 | 浏览 / 搜索 / 收藏 / 分类 |

---

## 🗂️ 项目结构

```
cookbook/
├── .env.example              # 环境变量模板（含微信 AppID/Secret）
├── .gitignore
├── config.py                 # Flask 配置：dev / prod + 微信配置
├── run.py                    # Flask 入口（支持 --prod）
├── requirements.txt
├── start.sh / stop.sh / build-weapp.sh
│
├── app/                      # Flask 后端
│   ├── __init__.py           # create_app + 5 个蓝图注册 + SPA fallback
│   ├── models.py             # User / Family / FamilyMember / Category / Recipe / DailyVote
│   ├── api/
│   │   ├── user.py           # 微信登录 / 账号注册登录 / 个人信息
│   │   ├── family.py         # 家庭：创建 / 加入 / 退出 / 成员
│   │   ├── vote.py           # 每日抽签：推荐 / 投票 / 结果 / 历史
│   │   ├── recipe.py
│   │   └── category.py
│   └── utils/
│       ├── jwt_util.py
│       └── response.py
│
└── web/                      # Taro 多端前端（Vue3 + TS）
    ├── src/
    │   ├── pages/
    │   │   ├── index/        # 首页（闪购风格推荐）
    │   │   ├── vote/         # 🎯 每日抽签投票（核心页面）
    │   │   ├── recipe/detail
    │   │   ├── family/bind   # 家庭绑定
    │   │   ├── family/mine   # 我的家庭
    │   │   ├── login/        # 微信登录
    │   │   └── mine/         # 我的
    │   ├── api/              # user / family / vote / recipe / category
    │   ├── stores/user.ts    # Pinia
    │   └── app.scss          # 红橙主题全局样式
    └── dist/                 # 构建产物
```

---

## 🚀 快速开始

### 后端

```bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env       # 修改 SECRET_KEY
python3 run.py             # http://127.0.0.1:5000
```

### 前端 H5

```bash
cd web && npm install && npm run dev:h5
# http://127.0.0.1:10086（自动代理 /api → Flask）
```

### 微信小程序

```bash
cd web && npm run dev:weapp
# 微信开发者工具 → 导入项目 → 目录选 web/
# 本地设置勾选 ✅ 不校验合法域名
```

---

## 📡 API 接口

### 认证
所有 `POST/GET` 带 `@login_required` 的接口，请求头加：
```
Authorization: Bearer <token>
```
返回 401 = token 过期/无效。

### 用户 `/api/user`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/wx-login` | **微信登录** `{code, nickname?, avatar?}` |
| POST | `/login` | 账号登录（开发用） |
| POST | `/register` | 账号注册（开发用） |
| GET | `/profile` | 个人信息 |
| PUT | `/profile` | 修改昵称/头像 |

**微信登录流程**：
```
小程序 wx.login() → 拿到 code
→ POST /api/user/wx-login {code, nickname, avatar}
→ 后端 code2session → 返回 token + user
→ 前端存 token 到 Storage
```
没配 `WX_APPID/WX_SECRET` 时自动降级为模拟登录（用 code 当 openid）。

### 家庭 `/api/family`

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/create` | 创建家庭 `{name}` → 返回邀请码 |
| POST | `/join` | 输入邀请码加入 `{invite_code}` |
| POST | `/leave` | 退出家庭 |
| GET | `/mine` | 我所在的家庭 + 成员列表 |
| GET | `/members` | 列出家庭成员 |
| PUT | `/update` | 修改家庭昵称（仅创建者） |

### 每日抽签 `/api/vote`

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/recommend` | 推荐菜谱池（4~12 个） |
| POST | `/cast` | 投票 / 改投 `{recipe_id}` |
| GET | `/today` | 今日结果（每个人投了啥 / 冠军） |
| GET | `/history?days=7` | 最近 N 天历史 |
| POST | `/cancel` | 取消今日投票 |

### 菜谱 / 分类（不变）

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/api/recipe/list` | `page&per_page&category_id&keyword` |
| GET | `/api/recipe/<id>` | 详情 |
| GET | `/api/recipe/random?count=1` | 随机推荐 |
| POST | `/api/recipe/add` | ✅ 新增 |
| PUT | `/api/recipe/edit/<id>` | ✅ 仅作者本人 |
| DELETE | `/api/recipe/delete/<id>` | ✅ 仅作者本人 |
| POST | `/api/recipe/collect/<id>` | ✅ 切换收藏 |
| GET | `/api/recipe/collect/list` | ✅ 收藏列表 |
| GET | `/api/recipe/mine` | ✅ 我发布的 |

---

## 🗄️ 数据库

开发环境默认 SQLite：`data/cook.db`

切换 MySQL：
```bash
# .env.production
DATABASE_URL=mysql+pymysql://user:password@host:3306/cookbook
```

微信小程序**必须**后端有 HTTPS 公网域名，且在小程序后台配置 `request 合法域名`。

---

## 🏭 生产部署

```bash
# 构建 H5
cd web && npm run build:h5     # → web/dist/ 用 Nginx 托管

# 后端（Gunicorn）
FLASK_ENV=prod python3 run.py --prod
# 监听 0.0.0.0:8000，4 workers
```

---

## 🛠️ 技术栈

**后端**：Flask 3 · Flask-SQLAlchemy · Flask-Migrate · Flask-CORS · PyMySQL · python-dotenv · PyJWT · requests（微信接口）

**前端**：Taro 4 · Vue 3 · TypeScript · Pinia · Sass

**多端**：微信小程序 · H5 · React Native

**风格**：淘宝闪购（红橙主题 #FF2D2D / #FF6A00）
