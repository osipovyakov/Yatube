from django.test import TestCase
from django.contrib.auth import get_user_model
from posts.models import Group, Post

User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='TestUser')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тест-1',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_post_model_str(self):
        post = PostModelTest.post
        expected_str = post.text
        self.assertEqual(expected_str, str(post))

    def test_group_model_str(self):
        group = PostModelTest.group
        expected_str = group.title
        self.assertEqual(expected_str, str(group))
