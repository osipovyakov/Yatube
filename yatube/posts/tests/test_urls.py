from django.urls import reverse
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Post, Group, Comment, Follow
from django.core.cache import cache


User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.wrong_user = User.objects.create_user(username='wrong_auth')
        cls. group = Group.objects.create(
            title='Тестовая группа',
            slug='Тест-1',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user
        )
        cls.comment = Comment.objects.create(
            author=cls.user,
            post=cls.post,
            text='Тестовый комментарий',
        )
        cls.url_index = reverse('posts:index')
        cls.url_create = reverse('posts:post_create')
        cls.url_post_edit = reverse(
            'posts:update_post', kwargs={'post_id': '1'})
        cls.url_about_author = reverse('about:author')
        cls.url_about_tech = reverse('about:tech')
        cls.url_group = reverse(
            'posts:group_list', kwargs={'slug': cls.group.slug})
        cls.url_post_detail = reverse(
            'posts:post_detail', kwargs={'post_id': '1'})
        cls.url_profile = reverse(
            'posts:profile', kwargs={'username': 'auth'})
        cls.url_comment = reverse(
            'posts:add_comment', kwargs={'post_id': '1'})
        cls.utl_follow = reverse(
            'posts:profile_follow', kwargs={'username': 'auth'})

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        user = URLTests.user
        wrong_user = URLTests.wrong_user
        self.authorized_client = Client()
        self.authorized_client.force_login(user)
        self.authorized_client_wrong = Client()
        self.authorized_client_wrong.force_login(wrong_user)

    def test_any_user_index_page(self):
        response_guest = self.guest_client.get(self.url_index)
        response_autorized = self.authorized_client.get(self.url_index)
        self.assertEqual(response_guest.status_code, 200)
        self.assertEqual(response_autorized.status_code, 200)

    def test_any_user_about_author(self):
        response_guest = self.guest_client.get(self.url_about_author)
        response_autorized = self.authorized_client.get(self.url_about_author)
        self.assertEqual(response_guest.status_code, 200)
        self.assertEqual(response_autorized.status_code, 200)

    def test_any_user_about_tech(self):
        response_guest = self.guest_client.get(self.url_about_tech)
        response_autorized = self.authorized_client.get(self.url_about_tech)
        self.assertEqual(response_guest.status_code, 200)
        self.assertEqual(response_autorized.status_code, 200)

    def test_any_user_group(self):
        response_guest = self.guest_client.get(self.url_group)
        response_autorized = self.authorized_client.get(self.url_group)
        self.assertEqual(response_guest.status_code, 200)
        self.assertEqual(response_autorized.status_code, 200)

    def test_any_user_post_detail(self):
        response_guest = self.guest_client.get(self.url_post_detail)
        response_autorized = self.authorized_client.get(self.url_post_detail)
        self.assertEqual(response_guest.status_code, 200)
        self.assertEqual(response_autorized.status_code, 200)

    def test_any_user_profile(self):
        response_guest = self.guest_client.get(self.url_profile)
        response_autorized = self.authorized_client.get(self.url_profile)
        self.assertEqual(response_guest.status_code, 200)
        self.assertEqual(response_autorized.status_code, 200)

    def test_non_existent_page(self):
        response_guest = self.guest_client.get('/test/')
        response_autorized = self.authorized_client.get('/test/')
        self.assertEqual(response_guest.status_code, 404)
        self.assertEqual(response_autorized.status_code, 404)

    def test_authorized_user_create(self):
        response_guest = self.guest_client.get(self.url_create)
        response_autorized = self.authorized_client.get(self.url_create)
        self.assertEqual(response_guest.status_code, 302)
        self.assertEqual(response_autorized.status_code, 200)

    def test_author_user_edit(self):
        response_guest = self.guest_client.get(self.url_post_edit)
        response_autorized = self.authorized_client.get(self.url_post_edit)
        response_wrong = self.authorized_client_wrong.get(self.url_post_edit)
        self.assertEqual(response_guest.status_code, 302)
        self.assertEqual(response_autorized.status_code, 200)
        self.assertEqual(response_wrong.status_code, 302)

    def test_comment(self):
        response_guest = self.guest_client.get(self.url_comment)
        response_autorized = self.authorized_client.get(self.url_comment)
        self.assertEqual(response_guest.status_code, 302)
        self.assertEqual(response_autorized.status_code, 302)

    def test_follow(self):
        Follow.objects.create(
            author=self.wrong_user,
            user=self.user,
        )
        response_guest = self.guest_client.get(self.utl_follow)
        response_autorized = self.authorized_client.get(
            self.utl_follow)
        self.assertEqual(response_guest.status_code, 302)
        self.assertEqual(response_autorized.status_code, 302)
