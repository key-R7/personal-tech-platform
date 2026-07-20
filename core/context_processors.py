SITE_PROFILE = {
    "name": "你的姓名",
    "role": "计算机科学与技术专业大三学生",
    "direction": "正在学习 Python、Django 与 Web 软件工程",
    "career_goal": "希望寻找 Python Web 开发方向的实习或初级开发机会。",
    "introduction": (
        "我正在通过持续开发个人技术平台，学习从需求分析、数据库设计、"
        "后端开发到测试与部署的完整流程。"
    ),
    "education": "学校与具体教育经历待补充",
    "github_url": "https://github.com/your-username",
    "email": "your-email@example.com",
    "learning_topics": [
        "Python与Django Web开发",
        "数据库与后端工程基础",
        "自动化测试与软件工程实践",
    ],
    "skills": [
        "Python基础与面向对象编程",
        "Django Templates与ORM",
        "HTML、CSS与Bootstrap",
        "Git与基础测试流程",
    ],
}


def site_profile(request):
    """Expose editable placeholder profile content to every template."""
    return {"site_profile": SITE_PROFILE}
