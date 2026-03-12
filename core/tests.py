"""
CultureLog 测试套件
覆盖：Models / Forms / Views（含认证、分页、搜索、编辑评论）
运行：python manage.py test core
"""

from datetime import date
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .forms import MediaItemForm, ReviewForm, UserRegistrationForm
from .models import Genre, MediaItem, Review, UserProfile


# ==============================================================
# Model Tests
# ==============================================================


class GenreModelTest(TestCase):
    """Genre 模型基本行为测试。"""

    def test_create_genre(self):
        genre = Genre.objects.create(name="Sci-Fi")
        self.assertEqual(str(genre), "Sci-Fi")

    def test_genre_name_unique(self):
        Genre.objects.create(name="Drama")
        with self.assertRaises(Exception):
            Genre.objects.create(name="Drama")


class MediaItemModelTest(TestCase):
    """MediaItem 模型测试。"""

    def setUp(self):
        self.genre = Genre.objects.create(name="Action")
        self.item = MediaItem.objects.create(
            title="Inception",
            type="Movie",
            description="A dream within a dream.",
            release_date=date(2010, 7, 16),
        )
        self.item.genres.add(self.genre)

    def test_str_returns_title(self):
        self.assertEqual(str(self.item), "Inception")

    def test_type_choices(self):
        self.assertIn(self.item.type, ["Book", "Movie"])

    def test_genre_many_to_many(self):
        self.assertIn(self.genre, self.item.genres.all())

    def test_optional_fields_blank(self):
        item = MediaItem.objects.create(title="Unknown", type="Book")
        self.assertEqual(item.description, "")
        self.assertIsNone(item.release_date)


class ReviewModelTest(TestCase):
    """Review 模型测试。"""

    def setUp(self):
        self.user = User.objects.create_user(username="alice", password="pass1234")
        self.item = MediaItem.objects.create(title="Dune", type="Book")
        self.review = Review.objects.create(
            rating=5,
            comment="Epic.",
            user=self.user,
            media_item=self.item,
        )

    def test_str(self):
        self.assertIn("alice", str(self.review))
        self.assertIn("Dune", str(self.review))

    def test_rating_range(self):
        self.assertGreaterEqual(self.review.rating, 1)
        self.assertLessEqual(self.review.rating, 5)

    def test_cascade_delete_user(self):
        self.user.delete()
        self.assertEqual(Review.objects.count(), 0)

    def test_cascade_delete_media_item(self):
        self.item.delete()
        self.assertEqual(Review.objects.count(), 0)


# ==============================================================
# Form Tests
# ==============================================================


class UserRegistrationFormTest(TestCase):
    """UserRegistrationForm 验证测试。"""

    def _valid_data(self, **kwargs):
        data = {
            "username": "bob",
            "email": "bob@example.com",
            "password": "securepass99",
            "confirm_password": "securepass99",
        }
        data.update(kwargs)
        return data

    def test_valid_form(self):
        form = UserRegistrationForm(data=self._valid_data())
        self.assertTrue(form.is_valid(), form.errors)

    def test_password_mismatch(self):
        form = UserRegistrationForm(data=self._valid_data(confirm_password="wrongpass"))
        self.assertFalse(form.is_valid())
        self.assertIn("__all__", form.errors)

    def test_missing_username(self):
        data = self._valid_data()
        data.pop("username")
        form = UserRegistrationForm(data=data)
        self.assertFalse(form.is_valid())


class ReviewFormTest(TestCase):
    """ReviewForm 验证测试。"""

    def test_valid_form(self):
        form = ReviewForm(data={"rating": 4, "comment": "Great!"})
        self.assertTrue(form.is_valid())

    def test_missing_rating(self):
        form = ReviewForm(data={"comment": "Good"})
        self.assertFalse(form.is_valid())

    def test_invalid_rating(self):
        form = ReviewForm(data={"rating": 9, "comment": "Too high"})
        self.assertFalse(form.is_valid())

    def test_empty_comment_allowed(self):
        form = ReviewForm(data={"rating": 3, "comment": ""})
        self.assertTrue(form.is_valid())


class MediaItemFormTest(TestCase):
    """MediaItemForm 验证测试。"""

    def test_valid_form(self):
        form = MediaItemForm(
            data={
                "title": "The Matrix",
                "type": "Movie",
                "description": "Simulated reality.",
                "release_date": "1999-03-31",
                "image_url": "",
                "genres": [],
            }
        )
        self.assertTrue(form.is_valid(), form.errors)

    def test_missing_title(self):
        form = MediaItemForm(data={"type": "Book"})
        self.assertFalse(form.is_valid())

    def test_invalid_type(self):
        form = MediaItemForm(data={"title": "X", "type": "Podcast"})
        self.assertFalse(form.is_valid())


# ==============================================================
# View Tests — helpers
# ==============================================================


def make_user(username="testuser", password="testpass123"):
    return User.objects.create_user(username=username, password=password)


def make_item(title="Test Movie", item_type="Movie"):
    return MediaItem.objects.create(title=title, type=item_type)


def make_review(user, item, rating=4, comment="Good"):
    return Review.objects.create(
        rating=rating, comment=comment, user=user, media_item=item
    )


# ==============================================================
# View Tests — Public
# ==============================================================


class HomeViewTest(TestCase):
    def test_get(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/home.html")

    def test_latest_items_in_context(self):
        make_item("Film A")
        response = self.client.get(reverse("home"))
        self.assertIn("latest_items", response.context)


class MediaListViewTest(TestCase):
    def setUp(self):
        make_item("Movie One", "Movie")
        make_item("Book One", "Book")

    def test_get_all(self):
        response = self.client.get(reverse("media_list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["items"].count(), 2)

    def test_filter_movie(self):
        response = self.client.get(reverse("media_list") + "?type=Movie")
        self.assertEqual(response.context["items"].count(), 1)
        self.assertEqual(response.context["items"].first().type, "Movie")

    def test_filter_book(self):
        response = self.client.get(reverse("media_list") + "?type=Book")
        self.assertEqual(response.context["items"].count(), 1)

    def test_search_by_title(self):
        response = self.client.get(reverse("media_list") + "?q=Movie")
        self.assertEqual(response.context["items"].count(), 1)

    def test_search_no_results(self):
        response = self.client.get(reverse("media_list") + "?q=zzznomatch")
        self.assertEqual(response.context["items"].count(), 0)

    def test_pagination_exists(self):
        # 创建足够多的条目触发分页（每页 12 条）
        for i in range(15):
            make_item(f"Extra {i}")
        response = self.client.get(reverse("media_list"))
        self.assertIn("page_obj", response.context)

    def test_invalid_filter_type_ignored(self):
        response = self.client.get(reverse("media_list") + "?type=Podcast")
        self.assertEqual(response.context["items"].count(), 2)


class MediaDetailViewTest(TestCase):
    def setUp(self):
        self.item = make_item()
        self.user = make_user()

    def test_get(self):
        response = self.client.get(reverse("media_detail", args=[self.item.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/media_detail.html")

    def test_404_for_nonexistent_item(self):
        response = self.client.get(reverse("media_detail", args=[9999]))
        self.assertEqual(response.status_code, 404)

    def test_post_review_authenticated(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("media_detail", args=[self.item.id]),
            {"rating": 4, "comment": "Nice"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Review.objects.count(), 1)

    def test_post_review_unauthenticated_redirects(self):
        response = self.client.post(
            reverse("media_detail", args=[self.item.id]),
            {"rating": 4, "comment": "Nice"},
        )
        self.assertRedirects(response, reverse("login"))
        self.assertEqual(Review.objects.count(), 0)

    def test_post_review_ajax_authenticated(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("media_detail", args=[self.item.id]),
            {"rating": 5, "comment": "Async add"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["review_count"], 1)
        self.assertIn("review_html", payload)

    def test_post_review_ajax_unauthenticated_returns_401(self):
        response = self.client.post(
            reverse("media_detail", args=[self.item.id]),
            {"rating": 5, "comment": "Blocked"},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            HTTP_ACCEPT="application/json",
        )
        self.assertEqual(response.status_code, 401)
        payload = response.json()
        self.assertFalse(payload["ok"])
        self.assertIn("login_url", payload)

    def test_review_form_has_cancel_button(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("media_detail", args=[self.item.id]))
        self.assertContains(response, 'id="review-cancel-btn"')


# ==============================================================
# View Tests — Authentication
# ==============================================================


class RegisterViewTest(TestCase):
    def test_get(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)

    def test_post_valid(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "newuser",
                "email": "new@example.com",
                "password": "newpass123",
                "confirm_password": "newpass123",
            },
        )
        self.assertEqual(User.objects.filter(username="newuser").count(), 1)
        self.assertRedirects(response, reverse("home"))

    def test_post_password_mismatch(self):
        self.client.post(
            reverse("register"),
            {
                "username": "baduser",
                "email": "",
                "password": "pass1",
                "confirm_password": "pass2",
            },
        )
        self.assertEqual(User.objects.filter(username="baduser").count(), 0)


class LoginViewTest(TestCase):
    def setUp(self):
        make_user()

    def test_get(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)

    def test_post_valid(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "testuser",
                "password": "testpass123",
            },
        )
        self.assertRedirects(response, reverse("home"))

    def test_post_invalid(self):
        response = self.client.post(
            reverse("login"),
            {
                "username": "testuser",
                "password": "wrongpassword",
            },
        )
        self.assertEqual(response.status_code, 200)  # 重新渲染登录页


class LogoutViewTest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.client.login(username="testuser", password="testpass123")

    def test_logout_redirects(self):
        response = self.client.get(reverse("logout"))
        self.assertRedirects(response, reverse("home"))

    def test_logout_unauthenticated_redirects_to_login(self):
        self.client.logout()
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)


# ==============================================================
# View Tests — Authenticated
# ==============================================================


class ProfileViewTest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.item = make_item()
        make_review(self.user, self.item)

    def test_unauthenticated_redirects(self):
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 302)

    def test_authenticated_shows_reviews(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("profile"))
        self.assertEqual(response.status_code, 200)
        self.assertIn("page_obj", response.context)
        self.assertIn("profile_form", response.context)

    def test_profile_post_updates_avatar(self):
        self.client.login(username="testuser", password="testpass123")
        self.client.post(
            reverse("profile"), {"avatar_url": "https://example.com/a.jpg"}
        )
        profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(profile.avatar_url, "https://example.com/a.jpg")


class AddMediaViewTest(TestCase):
    def setUp(self):
        self.user = make_user()

    def test_unauthenticated_redirects(self):
        response = self.client.get(reverse("add_media"))
        self.assertEqual(response.status_code, 302)

    def test_get_authenticated(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("add_media"))
        self.assertEqual(response.status_code, 200)

    def test_post_creates_item(self):
        self.client.login(username="testuser", password="testpass123")
        self.client.post(
            reverse("add_media"),
            {
                "title": "New Film",
                "type": "Movie",
                "description": "",
                "release_date": "",
                "image_url": "",
                "genres": [],
            },
        )
        self.assertEqual(MediaItem.objects.filter(title="New Film").count(), 1)

    def test_created_by_set_to_current_user(self):
        self.client.login(username="testuser", password="testpass123")
        self.client.post(
            reverse("add_media"),
            {
                "title": "My Film",
                "type": "Movie",
                "description": "",
                "release_date": "",
                "image_url": "",
                "genres": [],
            },
        )
        item = MediaItem.objects.get(title="My Film")
        self.assertEqual(item.created_by, self.user)


class DeleteMediaViewTest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.other = make_user(username="other", password="otherpass")
        self.staff = User.objects.create_user(
            username="admin", password="adminpass", is_staff=True
        )
        self.item = MediaItem.objects.create(
            title="Test Movie", type="Movie", created_by=self.user
        )

    def test_unauthenticated_redirects(self):
        response = self.client.post(reverse("delete_media", args=[self.item.id]))
        self.assertEqual(response.status_code, 302)

    def test_owner_can_delete(self):
        self.client.login(username="testuser", password="testpass123")
        self.client.post(reverse("delete_media", args=[self.item.id]))
        self.assertEqual(MediaItem.objects.count(), 0)

    def test_non_owner_gets_403(self):
        self.client.login(username="other", password="otherpass")
        response = self.client.post(reverse("delete_media", args=[self.item.id]))
        self.assertEqual(response.status_code, 403)
        self.assertEqual(MediaItem.objects.count(), 1)

    def test_staff_can_delete(self):
        self.client.login(username="admin", password="adminpass")
        self.client.post(reverse("delete_media", args=[self.item.id]))
        self.assertEqual(MediaItem.objects.count(), 0)

    def test_get_shows_confirmation(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.get(reverse("delete_media", args=[self.item.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "core/delete_media.html")


class EditReviewViewTest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.other = make_user(username="other", password="otherpass")
        self.item = make_item()
        self.review = make_review(self.user, self.item)

    def test_unauthenticated_redirects(self):
        response = self.client.get(reverse("edit_review", args=[self.review.id]))
        self.assertEqual(response.status_code, 302)

    def test_owner_can_edit(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("edit_review", args=[self.review.id]),
            {"rating": 2, "comment": "Changed my mind."},
        )
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 2)
        self.assertEqual(self.review.comment, "Changed my mind.")

    def test_non_owner_gets_403(self):
        self.client.login(username="other", password="otherpass")
        response = self.client.post(
            reverse("edit_review", args=[self.review.id]),
            {"rating": 1, "comment": "Not mine."},
        )
        self.assertEqual(response.status_code, 403)
        self.review.refresh_from_db()
        self.assertEqual(self.review.rating, 4)  # 未被修改


class ApiViewTest(TestCase):
    def setUp(self):
        self.user = make_user()
        self.item = make_item("API Movie", "Movie")
        make_review(self.user, self.item, rating=5, comment="API review")

    def test_api_media_list(self):
        response = self.client.get(reverse("api_media_list"))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertIn("items", payload)
        self.assertGreaterEqual(len(payload["items"]), 1)

    def test_api_media_detail(self):
        with patch(
            "core.views.fetch_external_media_data",
            return_value={"source": "iTunes Search API", "genre": "Drama"},
        ):
            response = self.client.get(reverse("api_media_detail", args=[self.item.id]))
        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["id"], self.item.id)
        self.assertIn("reviews", payload)
        self.assertEqual(payload["external_media"]["source"], "iTunes Search API")

    def test_media_detail_includes_external_media_context(self):
        with patch(
            "core.views.fetch_external_media_data",
            return_value={"source": "iTunes Search API", "genre": "Drama"},
        ):
            response = self.client.get(reverse("media_detail", args=[self.item.id]))
        self.assertEqual(response.status_code, 200)
        self.assertIn("external_media", response.context)

    def test_api_review_create_requires_login(self):
        response = self.client.post(
            reverse("api_review_create"),
            data='{"media_item_id": %d, "rating": 4, "comment": "new"}' % self.item.id,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 302)

    def test_api_review_create_json_authenticated(self):
        self.client.login(username="testuser", password="testpass123")
        response = self.client.post(
            reverse("api_review_create"),
            data='{"media_item_id": %d, "rating": 4, "comment": "new via api"}'
            % self.item.id,
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 201)
        payload = response.json()
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["review"]["media_item_id"], self.item.id)
