# 个人技术平台

这是一个用于求职展示和 Django 学习的个人技术平台，采用服务端模板实现个人介绍、技术文章、项目展示、登录和评论。当前已完成开发/生产配置拆分，并支持本地 SQLite 与可选 PostgreSQL 配置。

## 当前功能

- 首页、About 页面、统一导航和页脚
- 文章列表、详情、分类、标签、关键词搜索和分页
- 项目列表、详情和精选项目
- Django Admin 内容管理
- Django 内置登录和安全的 POST 退出
- 评论创建、作者删除和 staff 管理权限
- 自定义 404、500 页面和控制台日志
- 开发与生产环境设置拆分

公开文章必须同时满足 `status=published` 和 `published_at` 不为空。首页、列表、详情、搜索、筛选和评论入口统一使用 `Article.objects.public()`。

## 技术栈

- Python 3.12
- Django 5.2.16
- Django Templates
- Bootstrap 5.3.8 CDN
- SQLite（默认本地开发）
- PostgreSQL + Psycopg 3（可选配置）
- Django 内置测试框架

## 目录结构

```text
config/
  settings/
    base.py          # 共用设置和环境变量辅助函数
    development.py   # 本地开发：默认SQLite和DEBUG=True
    production.py    # 生产环境：强制PostgreSQL和DEBUG=False
  urls.py
  asgi.py
  wsgi.py
core/                # 首页、About、认证URL和公共上下文
blog/                # 文章、分类、标签和评论
projects/            # 项目展示
templates/           # 全局及页面模板
static/              # CSS和favicon
manage.py            # Django管理命令入口
```

## 创建环境并安装依赖

PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

如果系统禁止激活脚本，可以直接使用：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

## 环境变量和 `.env.example`

`.env.example` 是可提交的变量清单，只包含示例值。可以复制为本地 `.env`：

```powershell
Copy-Item .env.example .env
```

项目使用 Python 标准库读取环境变量，不会自动加载 `.env`。复制后仍需在当前 PowerShell 会话设置变量，或在部署平台的环境变量界面配置。`.env`、真实密钥和数据库密码不能提交到 Git。

例如生成并设置开发密钥：

```powershell
$env:DJANGO_SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
$env:DJANGO_DEBUG = "true"
$env:DJANGO_ALLOWED_HOSTS = "localhost,127.0.0.1"
```

开发设置存在明确标注的本地专用密钥，因此不设置 `DJANGO_SECRET_KEY` 也可以启动；建议仍练习通过环境变量设置。该默认值绝不会被生产设置使用。

## 默认SQLite开发方式

`manage.py`、`wsgi.py` 和 `asgi.py` 默认选择 `config.settings.development`。未设置 `DATABASE_ENGINE` 时使用项目根目录的 `db.sqlite3`：

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

主要页面：

- 首页：<http://127.0.0.1:8000/>
- 文章：<http://127.0.0.1:8000/articles/>
- 项目：<http://127.0.0.1:8000/projects/>
- About：<http://127.0.0.1:8000/about/>
- 登录：<http://127.0.0.1:8000/accounts/login/>
- 管理后台：<http://127.0.0.1:8000/admin/>

## 本地切换到PostgreSQL

先准备一个可访问的 PostgreSQL 数据库，再在当前终端设置：

```powershell
$env:DATABASE_ENGINE = "postgresql"
$env:DATABASE_NAME = "portfolio"
$env:DATABASE_USER = "portfolio_user"
$env:DATABASE_PASSWORD = "replace-with-real-password"
$env:DATABASE_HOST = "127.0.0.1"
$env:DATABASE_PORT = "5432"
python manage.py migrate
python manage.py runserver
```

端口会被校验并转换为整数。缺少字段、端口无效或引擎名称错误时，Django 会给出明确配置错误。本仓库只完成 PostgreSQL 配置支持；没有内置 PostgreSQL 服务，也不代表已经连接或迁移了真实 PostgreSQL 数据库。

## 生产设置

部署时显式选择生产模块：

```powershell
$env:DJANGO_SETTINGS_MODULE = "config.settings.production"
$env:DJANGO_SECRET_KEY = "replace-with-a-long-random-production-secret"
$env:DJANGO_ALLOWED_HOSTS = "portfolio.example.com"
$env:DATABASE_ENGINE = "postgresql"
$env:DATABASE_NAME = "portfolio"
$env:DATABASE_USER = "portfolio_user"
$env:DATABASE_PASSWORD = "replace-with-real-password"
$env:DATABASE_HOST = "database.example.com"
$env:DATABASE_PORT = "5432"
python manage.py check
```

生产配置具有以下约束：

- `DEBUG` 始终为 `False`；如果显式设置 `DJANGO_DEBUG=true` 会拒绝启动。
- `DJANGO_SECRET_KEY`、`DJANGO_ALLOWED_HOSTS` 和全部 PostgreSQL 连接字段必须提供。
- 生产环境强制 PostgreSQL，不会静默回退 SQLite。
- `SECURE_CONTENT_TYPE_NOSNIFF` 默认启用。
- 在 HTTPS 已真实可用后，设置 `DJANGO_HTTPS_ENABLED=true` 才会启用安全Cookie、HTTPS跳转和一年HSTS。
- 只有可信反向代理正确设置 `X-Forwarded-Proto` 时，才设置 `DJANGO_TRUST_PROXY_HEADER=true`。
- 跨源 POST 场景可用逗号分隔的 `CSRF_TRUSTED_ORIGINS`，例如 `https://portfolio.example.com`。

正式部署前还应执行 `python manage.py check --deploy`，确认HTTPS、代理、静态文件和平台日志。当前尚未实现 Docker、Gunicorn、Nginx 或 CI/CD。

## 内容管理、登录和评论

项目没有开放注册。管理员通过 `/admin/` 创建用户和内容，普通用户使用 `/accounts/login/` 登录。

- 评论作者来自 `request.user`，文章来自服务端URL，客户端不能伪造。
- 评论创建、删除和退出只接受 POST，并启用 CSRF 防护。
- 普通用户只能删除自己的评论，staff 可以删除任意评论。
- 评论使用 Django 默认模板转义，避免脚本注入。

## 检查和测试

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

测试不依赖本地 `db.sqlite3` 中的手工数据；Django 会建立并销毁独立测试数据库。

## 修改个人资料占位内容

首页、About页面和页脚共用的个人资料位于 `core/context_processors.py` 中的 `SITE_PROFILE`。

## 当前限制与下一步

- PostgreSQL配置尚未对真实服务器执行连接和迁移验证。
- Bootstrap依赖CDN，离线环境样式可能不完整。
- 尚未实现用户注册、评论回复/审核、图片上传和Markdown编辑器。
- 尚未配置Docker和正式部署流程。

下一阶段建议准备独立的 PostgreSQL 开发实例，验证迁移和数据导入，再选择部署平台完成生产环境检查。
