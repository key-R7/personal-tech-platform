from django.core.exceptions import ValidationError
from django.db import models


class SingletonContentModel(models.Model):
    """Base model that limits each page configuration to one database row."""

    singleton_key = models.PositiveSmallIntegerField(
        default=1,
        unique=True,
        editable=False,
    )
    updated_at = models.DateTimeField("更新时间", auto_now=True)

    class Meta:
        abstract = True

    def clean(self):
        super().clean()
        model = type(self)
        if model.objects.exclude(pk=self.pk).exists():
            raise ValidationError("此页面最多只能保存一条内容配置。")

    def save(self, *args, **kwargs):
        self.singleton_key = 1
        super().save(*args, **kwargs)


class HomePageContent(SingletonContentModel):
    role = models.CharField("个人定位", max_length=200)
    direction = models.CharField("技术方向", max_length=300)
    introduction = models.TextField("个人简介")
    career_goal = models.TextField("求职目标")

    class Meta:
        verbose_name = "首页内容"
        verbose_name_plural = "首页内容"

    def __str__(self):
        return "首页内容配置"


class AboutPageContent(SingletonContentModel):
    role = models.CharField("个人定位", max_length=200)
    direction = models.CharField("技术方向", max_length=300)
    introduction = models.TextField("个人简介")
    education = models.CharField("教育背景", max_length=300)
    education_detail = models.TextField("教育背景说明")
    courses = models.TextField(
        "主修课程",
        help_text="每行填写一项。",
    )
    experience_highlight = models.TextField("实践亮点")
    learning_topics = models.TextField(
        "当前学习方向",
        help_text="每行填写一项。",
    )
    skills = models.TextField(
        "技术能力",
        help_text="每行填写一项。",
    )
    languages = models.TextField(
        "语言能力",
        help_text="每行填写一项。",
    )
    interests = models.TextField(
        "兴趣爱好",
        help_text="每行填写一项。",
    )
    career_goal = models.TextField("求职目标")
    project_goal = models.TextField("平台建设目标")

    class Meta:
        verbose_name = "关于我内容"
        verbose_name_plural = "关于我内容"

    def __str__(self):
        return "关于我内容配置"
