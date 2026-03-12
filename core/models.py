"""
CultureLog 数据模型
包含三个核心模型：Genre、MediaItem、Review
"""

from django.db import models
from django.contrib.auth.models import User


class Genre(models.Model):
    """媒体类型标签，如 Sci-Fi、Drama、Action 等。"""

    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name


class MediaItem(models.Model):
    """图书或电影条目，可关联多个 Genre 标签。"""

    TYPE_CHOICES = [
        ("Book", "Book"),
        ("Movie", "Movie"),
    ]

    title = models.CharField(max_length=200)
    type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    description = models.TextField(blank=True)
    release_date = models.DateField(null=True, blank=True)
    image_url = models.URLField(max_length=500, blank=True)

    # M:N 关系：一个条目可属于多个类型标签
    genres = models.ManyToManyField(Genre, related_name="media_items", blank=True)

    # 记录条目创建者，删除用户时设为 NULL（不级联删除条目）
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="added_media",
    )

    def __str__(self):
        return self.title


class Review(models.Model):
    """用户对某个媒体条目的评分与评论。

    rating 取值范围：1–5。
    created_at 在首次保存时自动记录。
    """

    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    # 外键：删除用户或媒体条目时级联删除其评论
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reviews")
    media_item = models.ForeignKey(
        MediaItem, on_delete=models.CASCADE, related_name="reviews"
    )

    def __str__(self):
        return f"{self.user.username} - {self.media_item.title} ({self.rating})"


class UserProfile(models.Model):
    """扩展用户资料：用于展示个人头像。"""

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    avatar_url = models.URLField(max_length=500, blank=True)

    def __str__(self):
        return f"Profile<{self.user.username}>"
