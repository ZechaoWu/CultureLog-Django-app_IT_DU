"""
CultureLog 视图层
功能：主页、媒体列表（含搜索+分页）、详情、注册、登录、退出、
      个人主页（含分页）、添加媒体、删除媒体、编辑评论、错误页
"""

import json
from urllib.parse import quote_plus
from urllib.request import urlopen

from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import AuthenticationForm
from django.core.paginator import Paginator
from django.http import Http404, HttpResponseBadRequest, HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.template.loader import render_to_string
from django.http import JsonResponse
from django.urls import reverse

from .forms import MediaItemForm, ProfileForm, ReviewForm, UserRegistrationForm
from .models import Genre, MediaItem, Review, UserProfile

ITEMS_PER_PAGE = 12
REVIEWS_PER_PAGE = 8


def fetch_external_media_data(title, item_type):
    media_type = "movie" if item_type == "Movie" else "ebook"
    endpoint = (
        "https://itunes.apple.com/search?term="
        f"{quote_plus(title)}&media={media_type}&limit=1"
    )
    try:
        with urlopen(endpoint, timeout=4) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except Exception:
        return None

    results = payload.get("results") or []
    if not results:
        return None

    item = results[0]
    return {
        "source": "iTunes Search API",
        "title": item.get("trackName") or item.get("collectionName"),
        "artist": item.get("artistName"),
        "genre": item.get("primaryGenreName"),
        "release_date": item.get("releaseDate"),
        "description": item.get("longDescription") or item.get("description"),
        "preview_url": item.get("previewUrl"),
        "external_url": item.get("trackViewUrl") or item.get("collectionViewUrl"),
        "artwork_url": item.get("artworkUrl100") or item.get("artworkUrl60"),
    }


# ---- 公开页面 ----


def home(request):
    """主页：展示最新 6 条媒体条目。"""
    latest_items = MediaItem.objects.all().order_by("-release_date")[:6]
    return render(request, "core/home.html", {"latest_items": latest_items})


def media_list(request):
    """浏览页：支持按类型筛选、全文搜索（标题/描述）、分页。"""
    item_type = request.GET.get("type")
    query = request.GET.get("q", "").strip()

    items = MediaItem.objects.all().order_by("-release_date")

    if item_type in ["Book", "Movie"]:
        items = items.filter(type=item_type)

    if query:
        items = items.filter(title__icontains=query)

    paginator = Paginator(items, ITEMS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "core/media_list.html",
        {
            "items": page_obj.object_list,
            "page_obj": page_obj,
            "filter_type": item_type,
            "query": query,
        },
    )


def media_detail(request, item_id):
    """媒体详情页：展示条目信息、评论列表，并提供添加评论表单。"""
    item = get_object_or_404(MediaItem, pk=item_id)
    reviews = item.reviews.all().order_by("-created_at")
    external_media = fetch_external_media_data(item.title, item.type)

    is_ajax = request.headers.get("x-requested-with") == "XMLHttpRequest"

    if request.method == "POST":
        if not request.user.is_authenticated:
            if is_ajax:
                return JsonResponse(
                    {
                        "ok": False,
                        "error": "Authentication required",
                        "login_url": f"{reverse('login')}?next={request.path}",
                    },
                    status=401,
                )
            return redirect("login")
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.media_item = item
            review.save()

            if is_ajax:
                review_html = render_to_string(
                    "core/includes/_review_card.html",
                    {
                        "review": review,
                        "user": request.user,
                    },
                    request=request,
                )
                return JsonResponse(
                    {
                        "ok": True,
                        "review_html": review_html,
                        "review_count": item.reviews.count(),
                    }
                )

            return redirect("media_detail", item_id=item.id)
        if is_ajax:
            return JsonResponse(
                {
                    "ok": False,
                    "errors": form.errors,
                },
                status=400,
            )
    else:
        form = ReviewForm()

    return render(
        request,
        "core/media_detail.html",
        {
            "item": item,
            "reviews": reviews,
            "form": form,
            "external_media": external_media,
        },
    )


# ---- 认证 ----


def register(request):
    """用户注册：创建账号后自动登录并跳转主页。"""
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data["password"])
            user.save()
            UserProfile.objects.get_or_create(user=user)
            login(request, user)
            return redirect("home")
    else:
        form = UserRegistrationForm()
    return render(request, "core/register.html", {"form": form})


def user_login(request):
    """用户登录：验证通过后跳转主页。"""
    if request.method == "POST":
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get("username")
            password = form.cleaned_data.get("password")
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("home")
    else:
        form = AuthenticationForm()
    return render(request, "core/login.html", {"form": form})


@login_required
def user_logout(request):
    """退出登录后跳转主页。"""
    logout(request)
    return redirect("home")


# ---- 登录后功能 ----


@login_required
def profile(request):
    """个人主页：展示当前用户所有评论（分页）。"""
    profile_obj, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == "POST":
        profile_form = ProfileForm(request.POST, instance=profile_obj)
        if profile_form.is_valid():
            profile_form.save()
            return redirect("profile")
    else:
        profile_form = ProfileForm(instance=profile_obj)

    user_reviews = Review.objects.filter(user=request.user).order_by("-created_at")
    paginator = Paginator(user_reviews, REVIEWS_PER_PAGE)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    return render(
        request,
        "core/profile.html",
        {
            "reviews": page_obj.object_list,
            "page_obj": page_obj,
            "total_reviews": user_reviews.count(),
            "profile_obj": profile_obj,
            "profile_form": profile_form,
        },
    )


@login_required
def add_media(request):
    """添加新媒体条目；成功后跳转至该条目详情页。"""
    if request.method == "POST":
        form = MediaItemForm(request.POST)
        if form.is_valid():
            item = form.save(commit=False)
            item.created_by = request.user
            item.save()
            form.save_m2m()
            return redirect("media_detail", item_id=item.id)
    else:
        form = MediaItemForm()
    return render(request, "core/add_media.html", {"form": form})


@login_required
def delete_media(request, item_id):
    """删除媒体条目（需确认）。仅条目创建者或管理员可操作。"""
    item = get_object_or_404(MediaItem, pk=item_id)
    if item.created_by != request.user and not request.user.is_staff:
        return HttpResponseForbidden("你没有权限删除此条目。")
    if request.method == "POST":
        item.delete()
        return redirect("media_list")
    return render(request, "core/delete_media.html", {"item": item})


@login_required
def edit_review(request, review_id):
    """编辑评论：只有评论作者本人可操作，其他用户返回 403。"""
    review = get_object_or_404(Review, pk=review_id)
    if review.user != request.user:
        return HttpResponseForbidden("你没有权限编辑此评论。")

    if request.method == "POST":
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect("media_detail", item_id=review.media_item.id)
    else:
        form = ReviewForm(instance=review)

    return render(
        request,
        "core/edit_review.html",
        {
            "form": form,
            "review": review,
        },
    )


# ---- 错误页（仅在 DEBUG=False 时生效）----


def error_404(request, exception):
    """自定义 404 页面。"""
    return render(request, "404.html", status=404)


def error_500(request):
    """自定义 500 页面。"""
    return render(request, "500.html", status=500)


def api_media_list(request):
    """最小 REST API: 媒体列表。"""
    items = MediaItem.objects.all().order_by("-release_date")
    payload = [
        {
            "id": item.id,
            "title": item.title,
            "type": item.type,
            "description": item.description,
            "release_date": item.release_date.isoformat()
            if item.release_date
            else None,
            "image_url": item.image_url,
        }
        for item in items
    ]
    return JsonResponse({"items": payload})


def api_media_detail(request, item_id):
    """最小 REST API: 媒体详情。"""
    item = get_object_or_404(MediaItem, pk=item_id)
    external_media = fetch_external_media_data(item.title, item.type)
    payload = {
        "id": item.id,
        "title": item.title,
        "type": item.type,
        "description": item.description,
        "release_date": item.release_date.isoformat() if item.release_date else None,
        "image_url": item.image_url,
        "genres": [genre.name for genre in item.genres.all()],
        "reviews": [
            {
                "id": review.id,
                "rating": review.rating,
                "comment": review.comment,
                "created_at": review.created_at.isoformat(),
                "username": review.user.username,
            }
            for review in item.reviews.all().order_by("-created_at")
        ],
        "external_media": external_media,
    }
    return JsonResponse(payload)


@login_required
def api_review_create(request):
    """最小 REST API: 新建评论。"""
    if request.method != "POST":
        return HttpResponseBadRequest("POST required")

    if request.content_type == "application/json":
        try:
            data = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)
    else:
        data = {
            "media_item_id": request.POST.get("media_item_id"),
            "rating": request.POST.get("rating"),
            "comment": request.POST.get("comment", ""),
        }

    media_item_id = data.get("media_item_id")
    rating = data.get("rating")
    comment = data.get("comment", "")

    try:
        media_item = MediaItem.objects.get(pk=media_item_id)
    except MediaItem.DoesNotExist:
        return JsonResponse({"ok": False, "error": "Media item not found"}, status=404)

    form = ReviewForm({"rating": rating, "comment": comment})
    if not form.is_valid():
        return JsonResponse({"ok": False, "errors": form.errors}, status=400)

    review = form.save(commit=False)
    review.user = request.user
    review.media_item = media_item
    review.save()

    return JsonResponse(
        {
            "ok": True,
            "review": {
                "id": review.id,
                "rating": review.rating,
                "comment": review.comment,
                "username": review.user.username,
                "media_item_id": media_item.id,
            },
        },
        status=201,
    )
