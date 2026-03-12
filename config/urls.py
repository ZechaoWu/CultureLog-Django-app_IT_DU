"""
URL 配置 — CultureLog
"""

from django.contrib import admin
from django.urls import path
from core import views

# 自定义错误处理（仅 DEBUG=False 时生效）
handler404 = "core.views.error_404"
handler500 = "core.views.error_500"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", views.home, name="home"),
    path("browse/", views.media_list, name="media_list"),
    path("item/<int:item_id>/", views.media_detail, name="media_detail"),
    path("register/", views.register, name="register"),
    path("login/", views.user_login, name="login"),
    path("logout/", views.user_logout, name="logout"),
    path("profile/", views.profile, name="profile"),
    path("add/", views.add_media, name="add_media"),
    path("item/<int:item_id>/delete/", views.delete_media, name="delete_media"),
    path("review/<int:review_id>/edit/", views.edit_review, name="edit_review"),
    path("api/media/", views.api_media_list, name="api_media_list"),
    path("api/media/<int:item_id>/", views.api_media_detail, name="api_media_detail"),
    path("api/reviews/", views.api_review_create, name="api_review_create"),
]
