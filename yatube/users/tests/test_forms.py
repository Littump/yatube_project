from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..forms import CreationForm

User = get_user_model()


class PostCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form = CreationForm()

    def setUp(self):
        self.client = Client()

    def test_create_user(self):
        """Валидная форма создает запись в User."""
        users_count = User.objects.count()

        form_data = {
            'first_name': 'test_first_name',
            'last_name': 'test_last_name',
            'username': 'test_username',
            'email': 'test@test.com',
            'password1': 'passpass123',
            'password2': 'passpass123'
        }

        form = CreationForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Отправляем POST-запрос
        response = self.client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        # Проверяем, сработал ли редирект
        self.assertRedirects(response, reverse('posts:index'))
        # Проверяем, увеличилось ли число пользователей
        self.assertEqual(User.objects.count(), users_count + 1)
        # Проверяем, что создался пользователь с заданным слагом
        self.assertTrue(
            User.objects.filter(
                first_name='test_first_name',
                last_name='test_last_name',
                username='test_username',
                email='test@test.com'
            ).exists()
        )
