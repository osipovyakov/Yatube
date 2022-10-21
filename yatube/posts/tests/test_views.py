import shutil
import tempfile
from django.test import TestCase, Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from posts.models import Post, Group, Comment, Follow
from django.urls import reverse
from django import forms
from django.conf import settings
from django.core.cache import cache

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class ViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.image = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif')
        cls.user = User.objects.create_user(username='auth')
        cls.follow = User.objects.create_user(username='auth_2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тест-1',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.image,)
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

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        cache.clear()
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(self.follow)

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            self.url_index: 'posts/index.html',
            self.url_group: 'posts/group_list.html',
            self.url_profile: 'posts/profile.html',
            self.url_post_detail: 'posts/post_detail.html',
            self.url_post_edit: 'posts/create_post.html',
            self.url_create: 'posts/create_post.html',
            self.url_about_author: 'about/author.html',
            self.url_about_tech: 'about/tech.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_posts_index_page_show_correct_context(self):
        response = self.authorized_client.get(self.url_index)
        test_obj = response.context['page_obj'][0]
        self.assertEqual(test_obj, self.post)

    def test_posts_profile_page_show_correct_context(self):
        response = self.authorized_client.get(self.url_profile)
        test_obj = response.context['page_obj'][0]
        self.assertEqual(test_obj, self.post)

    def test_posts_group_list_page_show_correct_context(self):
        response = self.authorized_client.get(self.url_group)
        test_obj = response.context['page_obj'][0]
        self.assertEqual(test_obj, self.post)

    def test_posts_detail_page_show_correct_context(self):
        response = self.authorized_client.get(self.url_post_detail)
        test_obj = response.context['post']
        self.assertEqual(test_obj, self.post)

    def test_create_post_show_correct_context(self):
        response = self.authorized_client.get(self.url_create)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_post_show_correct_context(self):
        response = self.authorized_client.get(self.url_post_edit)
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField}
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_new_post_is_demonstrated(self):
        pages_list = (
            self.url_index,
            self.url_group,
            self.url_profile,
        )
        for tested_page in pages_list:
            response = self.authorized_client.get(tested_page)
            self.assertEqual(len(response.context['page_obj'].object_list), 1)

    def test_post_in_wrong_group(self):
        Group.objects.create(
            title='Тестовая группа_2',
            slug='Тест-2',
            description='Тестовое описание_2')
        response = self.guest_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': 'Тест-2'}))
        posts = response.context['page_obj']
        self.assertEqual(0, len(posts))

    def test_new_comment_is_demonstrated(self):
        response = self.guest_client.get(self.url_post_detail)
        comment = response.context.get('comments')
        self.assertTrue(comment.filter(text='Тестовый комментарий').exists())

    def test_authorized_client_can_follow(self):
        follow_count_1 = Follow.objects.count()
        Follow.objects.create(author=self.user, user=self.follow)
        follow_count_2 = Follow.objects.count()
        self.assertEqual(follow_count_1 + 1, follow_count_2)

    def test_authorized_client_can_unfollow(self):
        Follow.objects.create(author=self.user, user=self.follow)
        follow_count_1 = Follow.objects.count()
        Follow.objects.filter(author=self.user, user=self.follow).delete()
        follow_count_2 = Follow.objects.count()
        self.assertEqual(follow_count_1 - 1, follow_count_2)

    def test_new_post_demonstrated_for_followers(self):
        Follow.objects.create(author=self.user, user=self.follow)
        response = self.authorized_client_2.get(reverse(
            'posts:follow_index'))
        new_post = response.context['page_obj'][0]
        self.assertEqual(new_post, self.post)

    def test_post_not_found_for_unfollowers(self):
        response = self.authorized_client.get(reverse(
            'posts:follow_index'))
        new_post = response.context['page_obj']
        self.assertEqual(0, len(new_post))

    def test_cache_index(self):
        text = 'abc'
        Post.objects.create(text=text, author=self.user)
        self.authorized_client.get(reverse('posts:index'))
        Post.objects.all().delete()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertIn(text, str(response.content))

    def test_comment_create(self):
        Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group)
        comment_form = {'text': 'Тестовый комментарий', }
        response_guest = self.guest_client.post(reverse(
            'posts:add_comment', kwargs={'post_id': 2}),
            data=comment_form)
        response_authorized_client = self.authorized_client.post(reverse(
            'posts:add_comment', kwargs={'post_id': 2}),
            data=comment_form)
        self.assertEqual(response_guest.status_code, 302)
        self.assertEqual(response_authorized_client.status_code, 302)
        self.assertRedirects(
            response_guest, '/auth/login/?next=/posts/2/comment/')
        self.assertRedirects(response_authorized_client, '/posts/2/')


PAGE_TEST_OFFSET = 5


class ViewsTests_paginator(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тест-1',
            description='Тестовое описание'
        )
        for i in range(PAGE_TEST_OFFSET + settings.NUMBER_OF_POSTS):
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовый пост',
                group=cls.group)

    def test_first_page_contains_ten_records(self):
        reverse_list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        for reverse_name in reverse_list:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertEqual(len(
                    response.context['page_obj']), settings.NUMBER_OF_POSTS)

    def test_second_page_contains_five_records(self):
        reverse_list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile', kwargs={'username': self.user.username}),
        ]
        for reverse_name in reverse_list:
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name + '?page=2')
                self.assertEqual(len(
                    response.context['page_obj']), PAGE_TEST_OFFSET)
