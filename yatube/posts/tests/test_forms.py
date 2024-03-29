import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm, CommentForm
from ..models import Group, Post, Comment

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTests(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Title',
            slug='Slug',
            description='Description'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )
        cls.form = PostForm()

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.guest = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        text = 'Тестовый текст'
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'group': self.group.pk,
            'text': text,
            'image': uploaded,
        }

        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={'username': 'HasNoName'})
        )
        # Проверяем, увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count + 1)
        # Проверяем, что создалась запись с заданным слагом
        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                text=text,
                image='posts/small.gif'
            ).exists()
        )

    def test_create_post_not_with_image(self):
        form_data = {
            'group': self.group.pk,
            'text': 'Тестовый текст',
            'image': SimpleUploadedFile("file.txt", b"file_content"),
        }

        form = PostForm(data=form_data, files=form_data)
        self.assertFalse(form.is_valid())
        self.assertEqual(form.errors['image'],
                         [('Загрузите правильное изображение. '
                           'Файл, который вы загрузили, поврежден '
                           'или не является изображением.')])

    def test_edit_post(self):
        """Валидная форма создает запись в Post."""
        posts_count = Post.objects.count()
        text = 'Тестовый текст_2'
        form_data = {
            'group': self.group.pk,
            'text': text,
        }

        form = PostForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Отправляем POST-запрос
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': 1}),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={'post_id': 1})
        )
        # Проверяем, не увеличилось ли число постов
        self.assertEqual(Post.objects.count(), posts_count)
        # Проверяем, что изменилась запись с заданным слагом
        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                text=text,
            ).exists()
        )
        # Проверяем, что пропала запись с заданным слагом
        self.assertFalse(
            Post.objects.filter(
                group=self.group,
                text='Тестовый текст',
            ).exists()
        )

    def test_comment_guest(self):
        comments_count = self.post.comments.count()
        form_data = {
            'text': 'test'
        }
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.guest.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(self.post.comments.count(), comments_count)

    def test_comment_authorized_client(self):
        comments_count = self.post.comments.count()
        form_data = {
            'text': 'test'
        }
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())
        self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True
        )
        self.assertEqual(self.post.comments.count(), comments_count + 1)
        self.assertTrue(
            Comment.objects.filter(
                post=self.post,
                author=self.user,
                text='test',
            ).exists()
        )
