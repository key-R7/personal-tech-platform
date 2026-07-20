# 个人技术平台

这是一个使用 Python、Django Templates、Bootstrap 和 SQLite 构建的个人技术平台。当前已完成阶段4：内容展示、文章分类搜索分页、Django内置登录以及文章评论权限控制。

## 本地运行

PowerShell：

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
$env:DJANGO_SECRET_KEY = python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
python manage.py migrate
python manage.py runserver
```

CMD可以不激活虚拟环境，直接执行：

```bat
set "DJANGO_SECRET_KEY=django-insecure-local-development-only"
".venv\Scripts\python.exe" manage.py migrate
".venv\Scripts\python.exe" manage.py runserver
```

开发密钥只保存在当前终端会话中，不会写入源码。

## 修改个人资料占位内容

首页、About页面和页脚共用的个人资料位于`core/context_processors.py`中的`SITE_PROFILE`。

## 创建用户与管理内容

本阶段没有开放用户注册。请先创建管理员：

```powershell
python manage.py createsuperuser
```

管理员可以在`/admin/`创建其他用户、文章、分类、标签、评论和项目。普通用户可以通过`/accounts/login/`登录。

主要页面：

- 首页：`http://127.0.0.1:8000/`
- 文章：`http://127.0.0.1:8000/articles/`
- 项目：`http://127.0.0.1:8000/projects/`
- About：`http://127.0.0.1:8000/about/`
- 登录：`http://127.0.0.1:8000/accounts/login/`
- 管理后台：`http://127.0.0.1:8000/admin/`

## 文章与评论规则

- 公开文章必须同时满足“状态为已发布”和“发布时间不为空”。
- 文章列表每页5篇，可组合关键词、分类和标签查询。
- 游客可以阅读公开文章和评论，但不能发表评论或删除评论。
- 登录用户只能删除自己的评论。
- staff管理员可以删除任意评论。
- 评论创建与删除只接受POST请求，并受CSRF和服务端权限检查保护。

## 检查与测试

```powershell
python manage.py check
python manage.py test
```

## 当前未实现

用户注册、找回密码、第三方登录、评论回复、评论审核、图片上传、Markdown、Docker和生产部署将在后续阶段再考虑。
