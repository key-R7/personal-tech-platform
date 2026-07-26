from .context_processors import SITE_PROFILE
from .models import AboutPageContent, HomePageContent

HOME_FIELDS = ("role", "direction", "introduction", "career_goal")
ABOUT_TEXT_FIELDS = (
    "role",
    "direction",
    "introduction",
    "education",
    "education_detail",
    "experience_highlight",
    "career_goal",
)
ABOUT_LIST_FIELDS = (
    "courses",
    "learning_topics",
    "skills",
    "languages",
    "interests",
)


def _clean_lines(value):
    return [line.strip() for line in value.splitlines() if line.strip()]


def home_page_content():
    """Return the editable homepage values with verified static fallbacks."""
    content = {field: SITE_PROFILE[field] for field in HOME_FIELDS}
    configured_content = HomePageContent.objects.first()
    if configured_content:
        content.update(
            {
                field: getattr(configured_content, field)
                for field in HOME_FIELDS
            }
        )
    return content


def about_page_content():
    """Return editable About values, converting newline fields to lists."""
    content = {
        field: SITE_PROFILE[field]
        for field in (*ABOUT_TEXT_FIELDS, *ABOUT_LIST_FIELDS)
    }
    content["project_goal"] = (
        "通过这个平台持续展示文章、项目与学习成果，并建立完整的软件工程实践经验。"
    )
    configured_content = AboutPageContent.objects.first()
    if configured_content:
        content.update(
            {
                field: getattr(configured_content, field)
                for field in ABOUT_TEXT_FIELDS
            }
        )
        content["project_goal"] = configured_content.project_goal
        content.update(
            {
                field: _clean_lines(getattr(configured_content, field))
                for field in ABOUT_LIST_FIELDS
            }
        )
    return content
