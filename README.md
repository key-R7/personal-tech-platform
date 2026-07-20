# 个人技术平台

这是一个面向求职展示和 Django 学习的个人技术平台，使用服务端模板完成个人介绍、技术文章、项目展示、登录和评论功能。当前进入阶段5：测试补强、安全审查、异常页面和基础日志配置。

## 当前功能

- 首页、About 页面及统一导航和页脚
- 技术文章列表与详情
- 文章分类、标签、关键词搜索和每页5篇的分页
- 项目列表、项目详情和精选项目展示
- Django Admin 内容管理
- Django 内置用户登录和 POST 退出
- 登录用户发表评论、删除自己的评论
- staff 用户删除任意评论
- 自定义 404、500 页面和控制台错误日志

公开文章必须同时满足 `status=published` 和 `published_at` 不为空。该规则由 `Article.objects.public()` 集中维护，首页、列表、详情、搜索、筛选和评论入口均使用同一规则。

## 技术栈

- Python 3.12
- Django 5.2.16
- Django Templates
- Bootstrap 5.3.8 CDN
- SQLite（仅用于当前本地开发）
- Django 内置测试框架

## 目录结构

```text
config/       Django配置和根URL
core/         首页、About、认证URL和公共上下文
blog/         文章、分类、标签和评论
projects/     项目展示
templates/    全局及各页面模板
static/       CSS和favicon
manage.py     Django管理命令入口
```

## 本地安装和启动

在项目根目录使用 PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:DJANGO_SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
$env:DJANGO_DEBUG = "true"
$env:DJANGO_ALLOWED_HOSTS = "localhost,127.0.0.1"
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

如果 PowerShell 禁止激活脚本，可以直接使用虚拟环境解释器：

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py runserver
```

`.env.example` 只用于说明变量名称；项目没有安装读取 `.env` 的第三方库。变量需要在当前终端或部署平台中设置。不要把真实密钥写入 `.env.example` 或提交到 Git。

主要页面：

- 首页：<http://127.0.0.1:8000/>
- 文章：<http://127.0.0.1:8000/articles/>
- 项目：<http://127.0.0.1:8000/projects/>
- About：<http://127.0.0.1:8000/about/>
- 登录：<http://127.0.0.1:8000/accounts/login/>
- 管理后台：<http://127.0.0.1:8000/admin/>

## 内容管理、登录和评论

项目没有开放注册。管理员通过 `/admin/` 创建用户、文章、分类、标签、评论和项目，普通用户使用 `/accounts/login/` 登录。

- 游客可以阅读公开文章和评论，但不能发表评论或删除评论。
- 评论的 `author` 来自 `request.user`，`article` 来自服务端URL；客户端提交同名字段无效。
- 评论创建、删除和退出只接受 POST，并使用 Django CSRF 防护。
- 普通用户只能删除自己的评论，staff 可以删除任意评论。
- 评论使用 Django 默认模板转义，不允许通过 HTML 或脚本注入页面。

## 配置和安全措施

- `DJANGO_SECRET_KEY` 是必填环境变量，缺少时项目会明确停止启动。
- `DJANGO_DEBUG` 默认仅为本地开发开启；生产环境必须设置为 `false`。
- `DJANGO_ALLOWED_HOSTS` 使用逗号分隔；生产环境必须填写真实域名。
- `.env`、`.venv`、SQLite数据库、缓存、媒体、收集后的静态文件和日志文件均被 Git 忽略。
- 404和500页面不会显示 Traceback 或敏感配置。`DEBUG=True` 时 Django 为开发者显示调试页面，因此自定义500页通常只在 `DEBUG=False` 时出现。
- `django` 与 `blog` 的警告和错误输出到控制台。生产环境后续应由部署平台集中收集和保留日志。

## 检查和测试

```powershell
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test
```

测试覆盖公开文章规则、认证、评论字段伪造与越权、CSRF、XSS转义、HTTP方法、分类标签搜索分页、项目和公共页面，以及错误页面和环境配置解析。

## 修改个人资料占位内容

首页、About页面和页脚共用的个人资料位于 `core/context_processors.py` 中的 `SITE_PROFILE`。

## 当前限制

- SQLite只适合当前本地学习，不作为正式生产数据库。
- Bootstrap通过CDN加载，离线环境下样式可能不完整。
- 尚未实现用户注册、找回密码、邮件验证、评论回复或审核、图片上传和Markdown编辑器。
- 尚未配置PostgreSQL、Docker、Gunicorn、Nginx、CI/CD或正式部署。

## 下一阶段建议

在进入新业务功能前，优先完成 PostgreSQL 和生产部署配置，运行 `python manage.py check --deploy`，并在部署平台配置独立的密钥、域名、HTTPS和日志保留策略。
