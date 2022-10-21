import shutil
import tempfile
from django.test import TestCase, Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from posts.models import Post, Group
from django.urls import reverse
from django.conf import settings

User = get_user_model()
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class FormsTests(TestCase):
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
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тест-1',
            description='Тестовое описание')

    def setUp(self):
        self.guest_client = Client()
        user = FormsTests.user
        self.authorized_client = Client()
        self.authorized_client.force_login(user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тест текст нового поста',
            'author': self.user.id,
            'group': self.group.id}
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тест текст нового поста',
                author=self.user.id,
                group=self.group.id).exists())
        self.assertEqual(response.status_code, 200)

    def test_create_post_with_image(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тест текст нового поста',
            'author': self.user.id,
            'group': self.group.id,
            'image': self.image}
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True)
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': self.user}))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тест текст нового поста',
                author=self.user.id,
                group=self.group.id,
                image='posts/small.gif',).exists())
        self.assertEqual(response.status_code, 200)

    def test_new_post_with_wrong_image(self):
        small_not_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        wrong_image = SimpleUploadedFile(
            name='small.mp4',
            content=small_not_gif,
            content_type='image/mp4')
        form_data = {
            'group': self.group.id,
            'author': self.user.id,
            'text': 'Тестовый текст',
            'image': wrong_image,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data)
        self.assertFormError(
            response,
            'form',
            'image',
            "Формат файлов 'mp4' не поддерживается. Поддерживаемые форматы"
            + " файлов: 'bmp, dib, gif, tif, tiff, jfif, jpe, jpg, jpeg,"
            + " pbm, pgm, ppm, pnm, png, apng, blp, bufr, cur, pcx, dcx,"
            + " dds, ps, eps, fit, fits, fli, flc, ftc, ftu, gbr, grib,"
            + " h5, hdf, jp2, j2k, jpc, jpf, jpx, j2c, icns, ico, im, iim,"
            + " mpg, mpeg, mpo, msp, palm, pcd, pdf, pxr, psd, bw, rgb, rgba,"
            + " sgi, ras, tga, icb, vda, vst, webp, wmf, emf, xbm, xpm'.")

    def test_edit_post(self):
        new_post = Post.objects.create(
            text='Тест до редактирования',
            author=self.user)
        form_data = {
            'text': 'Тест после редактирования'}
        self.authorized_client.post(
            reverse('posts:update_post', kwargs={'post_id': new_post.id}),
            data=form_data,
            follow=True)
        edited_post = Post.objects.get(id=new_post.id)
        self.assertNotEqual(new_post.text, edited_post.text)
