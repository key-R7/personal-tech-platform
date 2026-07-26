from django import forms

from .models import SocialComment, SocialPost


class CirclePostForm(forms.ModelForm):
    class Meta:
        model = SocialPost
        fields = ("content", "image", "video")
        widgets = {
            "content": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "maxlength": 2000,
                    "placeholder": "分享学习进展或技术思考（最多2000字）",
                }
            ),
            "image": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".jpg,.jpeg,.png,.webp,image/jpeg,image/png,image/webp",
                }
            ),
            "video": forms.ClearableFileInput(
                attrs={
                    "class": "form-control",
                    "accept": ".mp4,.webm,video/mp4,video/webm",
                }
            ),
        }

    def clean_content(self):
        return self.cleaned_data.get("content", "").strip()


class SocialCommentForm(forms.ModelForm):
    content = forms.CharField(
        label="评论内容",
        max_length=500,
        strip=True,
        error_messages={"required": "评论内容不能为空。"},
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 2,
                "maxlength": 500,
                "placeholder": "写下评论（最多500字）",
            }
        ),
    )

    class Meta:
        model = SocialComment
        fields = ("content",)

    def clean_content(self):
        content = self.cleaned_data["content"].strip()
        if not content:
            raise forms.ValidationError("评论内容不能为空。")
        return content
