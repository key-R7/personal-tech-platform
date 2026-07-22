# 个人技术平台面试准备

回答时先说明真实需求和代码位置，再解释技术选择与权衡。不要背定义，也不要声称不存在的性能数据。

## 1. 为什么选择Django？

- 项目需要内容模型、后台管理、认证、Session、表单和服务端模板。
- Django内置能力可以覆盖第一版需求，减少不必要依赖，适合学习完整Web请求流程。
- 代价是框架约定较多，因此通过拆分App和测试保持结构清晰。

## 2. Django Project和App有什么区别？

- `config`是Project配置层，负责设置、根URL、WSGI和ASGI入口。
- `core`、`blog`、`projects`是按业务职责划分的App。
- App可以包含模型、视图、URL、Admin和测试；Project负责把它们组合起来。

## 3. 请求如何从URL到View再到Template？

- `config/urls.py`先匹配应用前缀，再进入App URLConf。
- 命名URL映射到View；View读取请求、查询ORM并组织Context。
- `render()`将Context交给继承`base.html`的Template，最终返回HTML响应。

## 4. ORM模型如何映射数据库表？

- 每个Model通常映射一张表，每个字段映射表列。
- Migration记录模型结构变化，`migrate`将变化应用到SQLite或PostgreSQL。
- ORM让业务查询不直接依赖某一种数据库SQL方言。

## 5. ForeignKey和ManyToManyField有什么区别？

- `Article.category`是ForeignKey：一篇文章最多属于一个分类，一个分类可以包含多篇文章。
- `Article.tags`是ManyToManyField：文章和标签双方都可以关联多条记录，中间表由Django维护。

## 6. 如何保证草稿文章不会泄露？

- `ArticleQuerySet.public()`同时过滤`status=published`和`published_at`非空。
- 首页、列表、详情、搜索、筛选和评论创建入口都从该QuerySet开始。
- 即使猜到草稿slug，公开详情仍返回404；相应行为有测试覆盖。

## 7. 为什么评论author不能由前端提交决定？

- 前端字段可以被用户伪造。
- `CommentForm`只接受正文，View在服务端把`request.user`设置为author。
- 所属文章也由URL中的slug经过公开文章查询得到，不能由客户端指定。

## 8. 如何防止用户删除其他人的评论？

- View读取目标评论后比较`request.user`与`comment.author`。
- 仅作者本人或`is_staff`用户可以删除，其他登录用户得到403。
- 前端隐藏按钮只是体验优化，真正权限判断在服务端。

## 9. 为什么删除操作使用POST？

- GET应当安全且幂等，浏览器预取、爬虫或链接访问不应修改数据。
- `@require_POST`拒绝GET删除，POST同时受CSRF保护。

## 10. CSRF防护是什么？

- CSRF攻击利用用户已登录的Cookie诱导浏览器向目标站点提交请求。
- Django中间件和模板中的`{% csrf_token %}`共同校验请求来自可信页面。
- 评论创建、删除、退出等状态修改请求均使用POST和CSRF Token。

## 11. Django模板如何降低XSS风险？

- Django模板默认转义变量中的HTML特殊字符。
- 评论正文直接以普通变量渲染，没有使用`safe`。
- 如果未来允许Markdown，应先使用受控解析器和HTML清理策略。

## 12. select_related和prefetch_related有什么区别？

- `select_related`通过SQL JOIN加载ForeignKey等单值关系，文章列表用于category。
- `prefetch_related`使用额外查询批量加载多值关系，文章列表用于tags。
- 两者避免在模板循环中为每篇文章重复查询，降低N+1问题。

## 13. SQLite和PostgreSQL有什么区别？

- SQLite是单文件数据库，配置简单，适合本地学习和测试。
- PostgreSQL是独立数据库服务，更适合并发、约束、备份和生产运维。
- 开发设置默认SQLite；生产设置强制PostgreSQL，避免静默回退。

## 14. 为什么使用环境变量？

- 密钥、主机名和数据库凭据随环境变化，不应写进仓库。
- `base.py`负责解析和校验，生产设置对缺失值明确失败。
- `.env.example`只列变量名和示例格式，不包含真实秘密。

## 15. Dockerfile和compose.yaml分别负责什么？

- Dockerfile描述单个Django镜像：Python、依赖、非root用户、入口和Gunicorn。
- Compose描述web、db、网络、健康检查、环境变量和PostgreSQL命名卷之间的关系。

## 16. Gunicorn和runserver有什么区别？

- `runserver`方便本地调试，不面向生产负载和进程管理。
- Gunicorn是WSGI服务器，负责管理worker、超时和访问日志。
- 容器使用Gunicorn，本地开发使用runserver。

## 17. PostgreSQL健康检查有什么作用？

- 容器“已启动”不等于数据库“可连接”。
- `pg_isready`让Compose等待数据库就绪后再启动web。
- Web入口仍进行有限重试，超时后失败退出而不是无限等待。

## 18. GitHub Actions执行哪些检查？

- 在PostgreSQL服务上安装依赖、检查敏感文件和Django配置。
- 检查遗漏迁移、执行迁移、确认`connection.vendor`为PostgreSQL并运行全部测试。
- 独立Job构建Docker镜像，但不推送镜像或自动部署。

## 19. 项目中遇到的主要问题及解决过程？

- 虚拟环境未激活导致Django导入失败：固定使用项目解释器并记录命令。
- 公开规则容易散落：提炼`Article.objects.public()`并补充草稿、空发布时间测试。
- 评论权限不能依赖按钮：在View中校验作者/staff并限制POST。
- SQLite与生产差异：拆分设置，通过Docker和CI在真实PostgreSQL上验证。
- 移动端出现轻微横向溢出：通过浏览器测量`scrollWidth`定位Bootstrap gutter并修正。

## 20. 项目下一步如何改进？

- 先完成公开仓库、CI绿色结果、真实截图和演示视频。
- 部署时接入托管PostgreSQL、HTTPS、日志和备份。
- 内容层面继续补充真实技术文章和项目，不急于增加点赞、消息队列等无关功能。
