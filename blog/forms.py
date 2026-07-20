from django import forms

from .models import Comment


class CommentForm(forms.ModelForm):
    content = forms.CharField(
        label="评论内容",
        max_length=500,
        strip=True,
        error_messages={"required": "评论内容不能为空"},
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 4,
                "maxlength": 500,
                "placeholder": "写下你的评论（最多500字）",
            }
        ),
    )

    class Meta:
        model = Comment
        fields = ("content",)

    def clean_content(self):
        content = self.cleaned_data["content"].strip()
        if not content:
            raise forms.ValidationError("评论内容不能为空")
        return content
