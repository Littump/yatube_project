from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()


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

    def setUp(self):
        # Создаем неавторизованный клиент
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Валидная форма создает запись в Post."""
        tasks_count = Post.objects.count()
        text = 'Тестовый текст'
        form_data = {
            'group': self.group.pk,
            'text': text
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
        self.assertEqual(Post.objects.count(), tasks_count + 1)
        # Проверяем, что создалась запись с заданным слагом
        self.assertTrue(
            Post.objects.filter(
                group=self.group,
                text=text,
            ).exists()
        )

    def test_edit_post(self):
        """Валидная форма создает запись в Post."""
        tasks_count = Post.objects.count()
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
        self.assertEqual(Post.objects.count(), tasks_count)
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
