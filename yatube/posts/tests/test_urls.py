from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from http import HTTPStatus

from ..models import Group, Post


User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=PostURLTests.user
        )
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='slug',
            description='Тестовое описание'
        )

    def setUp(self):
        self.guest_client = Client()
        self.user_no_author = User.objects.create_user(username='HasNoName2')
        self.authorized_client_no_author = Client()
        self.authorized_client_no_author.force_login(self.user_no_author)
        self.authorized_client_author = Client()
        self.authorized_client_author.force_login(self.user)

    def test_home_url_exists_at_desired_location(self):
        """Страница / доступна любому пользователю."""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_slug_url_exists_at_desired_location(self):
        """Страница /group/slug/ доступна любому пользователю."""
        response = self.guest_client.get(f'/group/{self.group.slug}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_username_url_exists_at_desired_location(self):
        """Страница /profile/username/ доступна любому пользователю."""
        response = self.guest_client.get(
            f'/profile/{self.user.username}/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_posts_id_url_exists_at_desired_location(self):
        """Страница /posts/id/ доступна любому пользователю."""
        response = self.guest_client.get(f'/posts/{self.post.id}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_unexisting_page_url_exists_at_desired_location(self):
        """Страница /unexisting_page/ доступна любому пользователю (ошибка)."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_create_url_exists_at_desired_location(self):
        """Страница /create/ доступна авторизованному пользователю."""
        response = self.authorized_client_no_author.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_url_redirect_anonymous_on_admin_login(self):
        """Страница по адресу /create/ перенаправит
        анонимного пользователя на страницу логина. """
        response = self.guest_client.get('/create/', follow=True)
        self.assertRedirects(
            response, '/auth/login/?next=/create/'
        )

    def test_edit_url_exists_at_desired_location(self):
        """Страница /posts/id/edit/ доступна
        авторизованному пользователю (автору)."""
        response = self.authorized_client_author.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_edit_url_redirect_anonymous_on_posts_id(self):
        """Страница по адресу /posts/id/edit/ перенаправит
        анонимного пользователя на логин"""
        response = self.guest_client.get(
            f'/posts/{self.post.id}/edit/', follow=True
        )
        self.assertRedirects(
            response, f'/auth/login/?next=/posts/{self.post.id}/edit/'
        )

    def test_edit_url_redirect_no_author_on_posts_id(self):
        """Страница по адресу /posts/id/edit/ перенаправит
        не автора поста на страницу поста."""
        response = self.authorized_client_no_author.get(
            f'/posts/{self.post.id}/edit/'
        )
        self.assertRedirects(
            response, f'/posts/{self.post.id}/'
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client_author.get(address)
                self.assertTemplateUsed(response, template)
