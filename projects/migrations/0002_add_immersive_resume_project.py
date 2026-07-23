from django.db import migrations


PROJECT_SLUG = "immersive-ai-resume"


def add_immersive_resume_project(apps, schema_editor):
    Project = apps.get_model("projects", "Project")
    Project.objects.get_or_create(
        slug=PROJECT_SLUG,
        defaults={
            "title": "3D 双语个人简历网站",
            "summary": (
                "使用 Next.js 与 TypeScript 构建的中英文个人简历网站，"
                "结合 3D 场景、动态背景和响应式内容展示。"
            ),
            "description": (
                "这是一个面向求职展示的沉浸式个人主页，提供 /zh 与 /en "
                "双语路由以及项目详情页。\n\n"
                "首屏使用程序化视觉组件，正文保留为可访问、可索引的语义化 "
                "HTML；页面会根据 WebGL 支持、设备性能、省流模式和"
                "减少动态效果偏好进行降级。\n\n"
                "个人资料集中维护在 content/resume.ts，并包含 sitemap、"
                "robots、Open Graph、单元测试和端到端测试配置。"
                "目前项目仍处于本地开发阶段，尚未建立公开 Git 仓库和"
                "在线演示地址。"
            ),
            "tech_stack": (
                "Next.js、React、TypeScript、Tailwind CSS、Three.js、"
                "React Three Fiber、Motion、OGL、Vitest、Playwright"
            ),
            "github_url": "",
            "demo_url": "",
            "status": "developing",
            "featured": True,
        },
    )


def remove_immersive_resume_project(apps, schema_editor):
    Project = apps.get_model("projects", "Project")
    Project.objects.filter(slug=PROJECT_SLUG).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("projects", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(
            add_immersive_resume_project,
            remove_immersive_resume_project,
        ),
    ]
