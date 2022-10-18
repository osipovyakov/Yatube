from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from posts.models import Post, Group
from django.core.cache import cache

User = get_user_model()


class URLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.wrong_user = User.objects.create_user(username='wrong_auth')
        Group.objects.create(
            title='Тестовая группа',
            slug='Тест-1',
            description='Тестовое описание'
        )
        Post.objects.create(
            text='Тестовый пост',
            author=cls.user
        )

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        user = URLTests.user
        wrong_user = URLTests.wrong_user
        self.authorized_client = Client()
        self.authorized_client.force_login(user)
        self.authorized_client_wrong = Client()
        self.authorized_client_wrong.force_login(wrong_user)

    def test_any_user(self):
        url_names = (
            '/',
            '/about/author/',
            '/about/tech/',
            '/group/Тест-1/',
            '/posts/1/',
            '/profile/auth/'
        )
        for address in url_names:
            with self.subTest(address=address):
                response_guest = self.guest_client.get(address)
                response_autorized = self.authorized_client.get(address)
                self.assertEqual(response_guest.status_code, 200)
                self.assertEqual(response_autorized.status_code, 200)

    def test_non_existent_page(self):
        response_guest = self.guest_client.get('/test/')
        response_autorized = self.authorized_client.get('/test/')
        self.assertEqual(response_guest.status_code, 404)
        self.assertEqual(response_autorized.status_code, 404)

    def test_authorized_user_create(self):
        response_guest = self.guest_client.get('/create/')
        response_autorized = self.authorized_client.get('/create/')
        self.assertEqual(response_guest.status_code, 302)
        self.assertEqual(response_autorized.status_code, 200)

    def test_author_user_edit(self):
        response_guest = self.guest_client.get('/posts/1/edit/')
        response_autorized = self.authorized_client.get('/posts/1/edit/')
        response_wrong = self.authorized_client_wrong.get('/posts/1/edit/')
        self.assertEqual(response_guest.status_code, 302)
        self.assertEqual(response_autorized.status_code, 200)
        self.assertEqual(response_wrong.status_code, 302)
