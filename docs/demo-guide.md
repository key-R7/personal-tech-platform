# 项目演示指南

## 本地准备

```powershell
.\.venv\Scripts\Activate.ps1
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

`seed_demo`只创建带`[演示]`前缀的简短内容，不创建用户或密码，不覆盖相同slug的已有内容，可重复执行。正式截图优先使用作者维护的真实项目和文章。

## 2—4分钟演示顺序

1. 首页：个人定位、最近文章和精选项目。
2. 文章列表：关键词搜索、分类、标签和分页参数保留。
3. 文章详情：公开规则、分类标签与评论区域。
4. 登录与评论：作者由服务端确定，删除只接受POST。
5. 项目展示：项目状态、技术栈和可选外链。
6. Admin：文章、分类、标签、评论和项目维护。
7. 工程化：测试数量、PostgreSQL、Docker和GitHub Actions。

## 截图清单

仓库截图统一放在`docs/images/`：

- `home.png`
- `articles.png`
- `article-detail.png`
- `article-filter.png`
- `projects.png`
- `comments.png`
- `admin.png`

截图不得包含密码、Cookie、真实数据库凭据、本地文件路径或多余浏览器界面。评论和Admin截图可使用临时本地账号，完成后删除。

## 手动验收重点

- 草稿和没有发布时间的文章无法公开访问。
- 登录、退出、评论创建和删除符合权限规则。
- 普通用户不能删除他人评论，staff可以管理评论。
- 390px手机宽度无横向滚动。
- GitHub Actions只有在GitHub页面真实显示绿色后才算通过。
