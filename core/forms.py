"""
CultureLog 表单
包含：UserRegistrationForm、ReviewForm、MediaItemForm
"""

from django import forms
from django.contrib.auth.models import User
from .models import MediaItem, Review, UserProfile


class UserRegistrationForm(forms.ModelForm):
    """新用户注册表单，包含密码确认校验。"""

    password = forms.CharField(widget=forms.PasswordInput, label="Password")
    confirm_password = forms.CharField(
        widget=forms.PasswordInput, label="Confirm Password"
    )

    class Meta:
        model = User
        fields = ["username", "email", "password"]

    def clean(self):
        """校验两次输入的密码是否一致。"""
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")
        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data


class ReviewForm(forms.ModelForm):
    """用户评论表单（评分 + 文字评论）。"""

    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "comment": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Write your review here...",
                }
            ),
        }


class MediaItemForm(forms.ModelForm):
    """添加新媒体条目的表单。"""

    class Meta:
        model = MediaItem
        fields = ["title", "type", "description", "release_date", "image_url", "genres"]
        widgets = {
            "description": forms.Textarea(
                attrs={
                    "rows": 4,
                    "placeholder": "Brief description...",
                }
            ),
            "release_date": forms.DateInput(attrs={"type": "date"}),
            "image_url": forms.URLInput(
                attrs={
                    "placeholder": "https://example.com/image.jpg",
                }
            ),
            "genres": forms.CheckboxSelectMultiple(),
        }


class ProfileForm(forms.ModelForm):
    """用户资料编辑表单：当前用于设置头像 URL。"""

    class Meta:
        model = UserProfile
        fields = ["avatar_url"]
        widgets = {
            "avatar_url": forms.URLInput(
                attrs={
                    "placeholder": "https://example.com/avatar.jpg",
                }
            )
        }
