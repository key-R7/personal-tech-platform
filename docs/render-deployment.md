# Render公网部署清单

本文档对应当前仓库的Docker部署方式。它不会替代Render控制台操作，也不表示项目已经成功部署。

## 1. 当前部署结构

```text
浏览器
  → Render HTTPS负载均衡器
  → Docker Web Service
  → Gunicorn
  → Django + WhiteNoise
  → Render PostgreSQL（同区域内部网络）
```

- Render构建仓库根目录的`Dockerfile`。
- Gunicorn监听`0.0.0.0:$PORT`；本地未提供`PORT`时回退到`8000`。
- `docker/entrypoint.sh`等待数据库就绪，然后执行迁移和`collectstatic`。
- WhiteNoise从`STATIC_ROOT`提供应用及Django Admin静态文件。
- PostgreSQL保存文章、项目、用户、Session和评论；不要在Render使用SQLite。

## 2. 创建Render PostgreSQL

1. 在Render Dashboard选择`New > Postgres`。
2. 数据库与Web Service选择同一区域，以使用内部网络。
3. 创建后打开数据库的连接信息，记录内部连接对应的数据库名、用户名、密码、主机和端口。
4. 不要把连接信息复制到README、提交记录、截图或聊天公开内容中。

Render免费PostgreSQL当前会在创建30天后过期，且不提供备份，只适合作品演示和学习。长期展示应升级数据库或准备迁移与备份方案。

## 3. 创建Docker Web Service

1. 在Render Dashboard选择`New > Web Service`。
2. 连接GitHub仓库并选择`main`分支。
3. Runtime选择`Docker`，Dockerfile路径保持仓库根目录的`./Dockerfile`。
4. Health Check Path填写`/`。
5. 首次部署建议只使用一个实例。
6. Docker部署不需要填写Build Command或Start Command：Render构建Dockerfile，并执行其中的`CMD`。

Render会自动提供`PORT`，不要在控制台把它写死为本地Compose的`WEB_PORT`。

## 4. Web Service环境变量

以下变量必须在Render Web Service的Environment页面配置。示例中的域名需要替换为Render实际分配的域名。

| 变量 | 填写规则 |
| --- | --- |
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` |
| `DJANGO_SECRET_KEY` | 使用Render生成的长随机值，不复用本地或CI密钥 |
| `DJANGO_DEBUG` | `false` |
| `DJANGO_ALLOWED_HOSTS` | 仅主机名，例如`your-service.onrender.com`；增加自定义域名时用逗号追加 |
| `CSRF_TRUSTED_ORIGINS` | 完整HTTPS来源，例如`https://your-service.onrender.com` |
| `DATABASE_ENGINE` | `postgresql` |
| `DATABASE_NAME` | Render PostgreSQL内部连接的数据库名 |
| `DATABASE_USER` | Render PostgreSQL内部连接的用户名 |
| `DATABASE_PASSWORD` | Render PostgreSQL密码 |
| `DATABASE_HOST` | Render PostgreSQL内部主机名，不是`db`或`localhost` |
| `DATABASE_PORT` | Render PostgreSQL端口，通常为`5432` |
| `DJANGO_HTTPS_ENABLED` | `true` |
| `DJANGO_TRUST_PROXY_HEADER` | `true`，使Django信任Render负载均衡器传入的HTTPS协议头 |

Render自动提供的`PORT`无需手动创建。`POSTGRES_DB`、`POSTGRES_USER`、`POSTGRES_PASSWORD`和`WEB_PORT`只供本地Compose使用，不需要加入Render Web Service。

首次配置时先使用Render的`onrender.com`域名。添加自定义域名后，同时更新`DJANGO_ALLOWED_HOSTS`和`CSRF_TRUSTED_ORIGINS`。

## 5. 构建、迁移和启动

Docker Web Service的构建命令由Render管理，相当于：

```text
docker build .
```

当前入口脚本按顺序执行：

```text
等待PostgreSQL（最多60秒）
python manage.py migrate --noinput
python manage.py collectstatic --noinput
gunicorn config.wsgi:application --bind 0.0.0.0:$PORT
```

Render的Pre-Deploy Command适合单独执行迁移，但该功能不支持免费Web实例。当前项目为兼容免费单实例，在容器启动时执行迁移。不要在控制台再配置相同迁移命令，否则会重复执行。未来升级为多实例或付费服务时，应把迁移移动到：

```text
python manage.py migrate --noinput
```

的Pre-Deploy Command，并相应调整入口脚本，确保迁移只执行一次。

## 6. 首次部署日志检查

在Render Events或Logs中依次确认：

1. Docker镜像构建完成；
2. 输出`Database connection is ready.`；
3. 数据库迁移没有报错；
4. `collectstatic`成功；
5. Gunicorn监听Render提供的端口；
6. Health Check通过并生成公网URL。

任何一步失败都应先查看该次部署日志，不要连续重复部署。

部署前使用生产配置执行`python manage.py check --deploy`。当前本地验证没有错误，只有以下两类HSTS建议警告：

- `security.W005`：尚未对所有子域启用HSTS；
- `security.W021`：尚未声明加入浏览器HSTS预加载列表。

这两项是警告而不是启动错误。只有确认自定义域名及其全部子域永久使用HTTPS，并理解预加载的长期影响后，才应启用对应设置；不要只为消除警告而修改安全策略。

## 7. 安全创建管理员

不要在代码、环境变量、README或部署脚本中保存固定管理员密码。

付费Web实例可以在Render Shell中交互执行：

```text
python manage.py createsuperuser
```

免费Web实例不提供Render Shell。可以在本机终端临时设置生产配置以及Render PostgreSQL的外部连接字段，然后执行同一命令：

```powershell
$env:DJANGO_SETTINGS_MODULE = "config.settings.production"
$env:DJANGO_SECRET_KEY = "与Render Web Service一致的密钥"
$env:DJANGO_DEBUG = "false"
$env:DJANGO_ALLOWED_HOSTS = "your-service.onrender.com"
$env:DATABASE_ENGINE = "postgresql"
$env:DATABASE_NAME = "Render数据库名"
$env:DATABASE_USER = "Render数据库用户"
$env:DATABASE_PASSWORD = "Render数据库密码"
$env:DATABASE_HOST = "Render数据库外部主机"
$env:DATABASE_PORT = "Render数据库外部端口"
python manage.py createsuperuser
```

命令完成后关闭终端或删除当前会话中的数据库和密钥环境变量。不要把这些真实值写入`.env.example`。

## 8. 部署后验收

依次检查：

- 首页、About、导航和页脚；
- 文章列表、详情、分类、标签、搜索和分页；
- 项目列表和详情；
- 登录、POST退出、评论创建和评论删除权限；
- Django Admin登录和静态样式；
- 不存在的URL显示自定义404；
- 手机宽度没有横向溢出；
- 浏览器控制台没有静态文件404或重定向循环；
- Render日志没有`DisallowedHost`、CSRF或数据库连接错误。

部署成功后再把真实公网地址加入README和简历。不要在真实部署完成前声称已有在线演示。

## 9. 已知限制

- Render免费Web在无访问15分钟后会休眠，下一次访问可能需要约一分钟唤醒。
- 免费Web文件系统是临时的，不能在本地文件系统保存上传内容或SQLite数据库。
- 免费PostgreSQL会在30天后过期且没有备份。
- 当前项目没有文件上传，因此暂不需要对象存储。
- 当前启动迁移策略只面向免费单实例演示；多实例部署需要独立的迁移阶段。
