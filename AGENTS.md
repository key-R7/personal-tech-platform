## 项目目标

本项目是一个使用Python和Django开发的个人技术平台，主要用于求职作品展示，同时帮助项目作者学习完整的Web开发流程。

平台包含技术文章、项目展示、个人介绍、学习记录和管理后台。

## 项目阶段

项目采用渐进式开发。

第一版只包含：

* 首页
* 文章列表和详情
* 项目列表和详情
* 关于页面
* Django Admin

后续再加入：

* 分类和标签
* 搜索和分页
* 登录和评论
* PostgreSQL
* Docker
* CI/CD

## 技术约束

当前使用：

* Python
* Django
* Django Templates
* Bootstrap
* SQLite
* Django内置测试框架

未经明确要求，不要加入：

* React
* Vue
* Django REST Framework
* Redis
* Celery
* 微服务
* Kubernetes
* Elasticsearch
* AI接口

## 开发原则

1. 优先使用Django内置能力。
2. 保持实现简单，避免过度设计。
3. 一次任务只处理一个明确功能。
4. 不要修改与当前任务无关的文件。
5. 不要自动执行Git提交。
6. 不要删除现有功能，除非任务明确要求。
7. 修改前先检查现有代码。
8. 修改后运行相关测试。
9. 新增核心业务逻辑时应同步增加测试。
10. 不允许把密钥或密码提交到仓库。

## 代码规范

* 遵循PEP 8。
* 使用清晰、完整的变量和函数名称。
* 视图不应包含过多业务逻辑。
* 模型字段应提供清晰的含义。
* URL必须使用命名路由。
* 模板使用继承，公共结构放在base.html中。
* 用户输入必须经过表单验证。
* 权限验证必须在服务端执行。
* 不要只在前端隐藏按钮来实现权限控制。

## 推荐目录

* config：项目配置
* apps/core：首页和公共页面
* apps/blog：文章功能
* apps/projects：项目展示
* templates：全局模板
* static：静态文件
* tests或各App下的tests：测试代码

可以根据Django惯例适当调整，但不要增加没有实际用途的目录。

## 常用命令

安装依赖：

pip install -r requirements.txt

执行数据库迁移：

python manage.py migrate

检查项目配置：

python manage.py check

运行测试：

python manage.py test

启动开发服务器：

python manage.py runserver

## 每次任务的完成报告

完成代码修改后，必须输出：

1. 完成了什么；
2. 修改了哪些文件；
3. 为什么这样设计；
4. 执行了哪些命令；
5. 测试是否通过；
6. 仍存在哪些限制；
7. 建议的下一步；
8. 项目作者应理解的三个知识点。

如果无法运行测试，必须明确说明原因，不能声称测试通过。
