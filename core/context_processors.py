SITE_PROFILE = {
    "name": "吴柯毅",
    "role": "计算机科学与技术本科生 · 后端开发",
    "direction": "聚焦 Python 自动化、Django 后端与多 Agent 工作流",
    "career_goal": (
        "求职方向为后端开发，持续将自动化、AI Agent 与软件工程能力"
        "应用到真实业务场景中。"
    ),
    "introduction": (
        "对互联网与 AI 技术保持高度敏感，具备需求分析、方案落地和沟通协作能力。"
        "能够独立完成 Python 自动化工具，并设计、搭建和优化多 Agent 协作工作流。"
    ),
    "education": "2024年9月至今 · 东北林业大学 · 计算机科学与技术（本科）",
    "education_detail": (
        "中外合作全英文授课，具有全英文专业学习、小组项目与技术汇报经历，"
        "能够跟进海外技术资料并参与跨语言沟通。"
    ),
    "location": "哈尔滨",
    "email": "15840486398@163.com",
    "github_url": "",
    "experience_highlight": (
        "曾将某课程小组约4小时的英文文献批量整理工作压缩至15分钟，"
        "具备识别重复流程并将其标准化、自动化的意识与能力。"
    ),
    "learning_topics": [
        "Python自动化工具与Django后端开发",
        "单Agent工具调用与多Agent协作工作流",
        "数据库、软件工程与自动化测试实践",
    ],
    "skills": [
        "Python：自动化脚本、批量文件处理、数据爬取与Web UI自动化测试",
        "AI Agent：工具调用、多Agent协作工作流的设计、搭建与部署",
        "Linux与Shell编程，熟悉Java开发和大数据开发技术",
        "Office办公与英文技术文献阅读、整理",
    ],
    "courses": [
        "离散数学",
        "统计理论",
        "软件开发",
        "Linux与Shell编程",
        "计算机组成原理",
        "算法与数据结构",
        "数据通信和安全",
        "数据分析",
        "机器学习",
        "Java程序设计",
        "数据库系统原理",
        "软件工程",
        "Python",
        "大数据开发",
    ],
    "languages": [
        "CET-4、CET-6均通过",
        "英语流利交流与英文文献阅读",
        "日语基本交流",
    ],
    "interests": [
        "健身",
        "外语学习",
        "探索新事物",
    ],
}


def site_profile(request):
    """Expose the shared personal profile to every template."""
    return {"site_profile": SITE_PROFILE}
