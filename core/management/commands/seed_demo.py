"""Create concise, clearly labeled demo content for local evaluation."""

from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from blog.models import Article, Category, Tag
from projects.models import Project


DEMO_CATEGORIES = (
    {
        "slug": "demo-django-engineering",
        "name": "[演示] Django工程实践",
        "description": "用于演示文章分类、筛选和列表功能。",
    },
    {
        "slug": "demo-python-automation",
        "name": "[演示] Python自动化",
        "description": "用于演示自动化主题文章。",
    },
)

DEMO_TAGS = (
    ("demo-python", "[演示] Python"),
    ("demo-django", "[演示] Django"),
    ("demo-testing", "[演示] 测试"),
    ("demo-postgresql", "[演示] PostgreSQL"),
    ("demo-docker", "[演示] Docker"),
)

DEMO_ARTICLES = (
    {
        "slug": "demo-public-article-rules",
        "title": "[演示] 用QuerySet统一文章公开规则",
        "summary": "展示如何集中约束已发布状态和发布时间，避免草稿从不同入口泄露。",
        "content": (
            "本条内容用于演示文章详情、分类和标签。\n\n"
            "项目通过Article.objects.public()统一公开范围，首页、列表、详情和评论入口复用同一规则。"
        ),
        "category": "demo-django-engineering",
        "tags": ("demo-django", "demo-testing"),
        "days_ago": 1,
    },
    {
        "slug": "demo-comment-permissions",
        "title": "[演示] Django评论权限的服务端校验",
        "summary": "展示登录、POST限制、CSRF以及评论作者删除权限。",
        "content": (
            "本条内容用于演示评论区域。\n\n"
            "评论作者来自request.user，普通用户只能删除自己的评论，staff可以执行管理操作。"
        ),
        "category": "demo-django-engineering",
        "tags": ("demo-django", "demo-testing"),
        "days_ago": 2,
    },
    {
        "slug": "demo-docker-postgresql",
        "title": "[演示] 使用Docker Compose连接PostgreSQL",
        "summary": "展示Web与数据库服务、健康检查和数据持久化的基本关系。",
        "content": (
            "本条内容用于演示Docker与数据库主题。\n\n"
            "Compose等待PostgreSQL健康后启动Web服务，普通down命令会保留命名卷中的数据。"
        ),
        "category": "demo-django-engineering",
        "tags": ("demo-postgresql", "demo-docker"),
        "days_ago": 3,
    },
    {
        "slug": "demo-python-automation-review",
        "title": "[演示] 识别并自动化重复工作",
        "summary": "展示如何从重复步骤中提炼输入、处理过程和可验证输出。",
        "content": (
            "本条内容用于演示Python自动化主题。\n\n"
            "自动化脚本应先明确数据边界、失败处理和可重复执行要求，再逐步替代手工流程。"
        ),
        "category": "demo-python-automation",
        "tags": ("demo-python", "demo-testing"),
        "days_ago": 4,
    },
)

DEMO_PROJECTS = (
    {
        "slug": "demo-django-content-platform",
        "title": "[演示] Django内容平台",
        "summary": "用于演示项目卡片、精选状态和详情页面。",
        "description": "演示项目数据，不代表额外的真实线上产品。",
        "tech_stack": "Python、Django、PostgreSQL、Bootstrap",
        "status": Project.Status.MAINTAINING,
        "featured": True,
    },
    {
        "slug": "demo-python-automation-toolkit",
        "title": "[演示] Python自动化工具集",
        "summary": "用于演示开发中项目的状态和技术栈。",
        "description": "演示项目数据，用于验证项目列表在多条记录下的布局。",
        "tech_stack": "Python、自动化测试、文件处理",
        "status": Project.Status.DEVELOPING,
        "featured": True,
    },
    {
        "slug": "demo-agent-workflow-lab",
        "title": "[演示] Agent工作流实验",
        "summary": "用于演示非精选项目和维护状态。",
        "description": "演示项目数据，不包含虚构的源码或在线演示链接。",
        "tech_stack": "Python、工具调用、工作流设计",
        "status": Project.Status.DEVELOPING,
        "featured": False,
    },
)


class Command(BaseCommand):
    help = "创建不会覆盖现有内容、可重复执行的本地演示数据。"

    def handle(self, *args, **options):
        now = timezone.now()
        categories = {}
        for data in DEMO_CATEGORIES:
            category, _ = Category.objects.get_or_create(
                slug=data["slug"],
                defaults={
                    "name": data["name"],
                    "description": data["description"],
                },
            )
            categories[data["slug"]] = category

        tags = {}
        for slug, name in DEMO_TAGS:
            tag, _ = Tag.objects.get_or_create(slug=slug, defaults={"name": name})
            tags[slug] = tag

        created_articles = 0
        for data in DEMO_ARTICLES:
            article, created = Article.objects.get_or_create(
                slug=data["slug"],
                defaults={
                    "title": data["title"],
                    "summary": data["summary"],
                    "content": data["content"],
                    "category": categories[data["category"]],
                    "status": Article.Status.PUBLISHED,
                    "published_at": now - timedelta(days=data["days_ago"]),
                },
            )
            if created:
                article.tags.set(tags[tag_slug] for tag_slug in data["tags"])
                created_articles += 1

        created_projects = 0
        for data in DEMO_PROJECTS:
            _, created = Project.objects.get_or_create(
                slug=data["slug"],
                defaults={
                    "title": data["title"],
                    "summary": data["summary"],
                    "description": data["description"],
                    "tech_stack": data["tech_stack"],
                    "status": data["status"],
                    "featured": data["featured"],
                },
            )
            created_projects += int(created)

        self.stdout.write(
            self.style.SUCCESS(
                "演示数据准备完成："
                f"新增文章{created_articles}篇，新增项目{created_projects}个。"
            )
        )
