from http import HTTPStatus

from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache
from freezegun import freeze_time

from ..models import Group, Post, Follow

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Title',
            slug='Slug',
            description='Description'
        )
        cls.group_2 = Group.objects.create(
            title='Title2',
            slug='Slug2',
            description='Description2'
        )
        cls.post = Post.objects.create(
            text='Текст',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        cache.clear()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_pages_names = {
            reverse('posts:index'): (
                'posts/index.html'
            ),
            reverse('posts:group_posts', kwargs={'slug': 'Slug'}): (
                'posts/group_list.html'
            ),
            reverse('posts:profile', kwargs={'username': 'HasNoName'}): (
                'posts/profile.html'
            ),
            reverse('posts:post_detail', kwargs={'post_id': 1}): (
                'posts/post_detail.html'
            ),
            reverse('posts:post_edit', kwargs={'post_id': 1}): (
                'posts/create_post.html'
            ),
            reverse('posts:post_create'): (
                'posts/create_post.html'
            ),
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_show_correct_context_page_obj(self):
        reverses = [
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': 'Slug'}),
            reverse('posts:profile', kwargs={'username': 'HasNoName'}),
        ]
        for rev in reverses:
            response = self.authorized_client.get(rev)
            first_object = response.context['page_obj'][0]
            self.assertEqual(first_object.text, 'Текст')
            self.assertEqual(first_object.author, self.user)
            self.assertEqual(first_object.group, self.group)

    def test_group_list_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': 'Slug'})
        )
        self.assertEqual(response.context.get('group'), self.group)

    def test_profile_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': 'HasNoName'})
        )
        self.assertEqual(response.context['cnt_posts_user'], 1)
        self.assertEqual(response.context.get('author'), self.user)

    def test_post_detail_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': 1})
        )
        post = response.context.get('post')
        self.assertEqual(post.text, 'Текст')
        self.assertEqual(post.author, self.user)
        self.assertEqual(post.group, self.group)
        self.assertEqual(response.context['cnt_posts_user'], 1)

    def test_post_create_edit_show_correct_context_forms(self):
        """Шаблон post/edit сформирован с правильным контекстом (forms)."""
        reverses = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': 1})
        ]
        form_fields = {
            'group': forms.fields.ChoiceField,
            'text': forms.fields.CharField
        }
        for rev in reverses:
            response = self.authorized_client.get(rev)
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_post_edit_show_correct_context_no_forms(self):
        """Шаблон edit_post сформирован с правильным контекстом (no forms)."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={'post_id': 1})
        )
        self.assertEqual(response.context['is_edit'], 1)
        self.assertEqual(response.context['post_id'], 1)

    def test_new_post_not_in_other_group(self):
        response = self.authorized_client.get(
            reverse('posts:group_posts', kwargs={'slug': 'Slug2'})
        )
        self.assertEqual(len(response.context['page_obj']), 0)


class PaginatorViewsTest(TestCase):

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')

        cls.group = Group.objects.create(
            title='Title',
            slug='Slug',
            description='Description'
        )
        posts = []
        cnt_posts = 13
        for ind in range(cnt_posts):
            posts.append(Post(text=f'text_{ind}',
                              author=cls.user,
                              group=cls.group))
        with freeze_time("2022-01-01 00:00:00"):
            Post.objects.bulk_create(posts)

    def setUp(self):
        cache.clear()
        self.client = Client()
        self.client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        reverses = [
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': 'Slug'}),
            reverse('posts:profile', kwargs={'username': 'HasNoName'})
        ]
        with freeze_time("2022-01-01 00:00:30"):
            for rev in reverses:
                response = self.client.get(rev)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_ten_records(self):
        reverses = [
            reverse('posts:index'),
            reverse('posts:group_posts', kwargs={'slug': 'Slug'}),
            reverse('posts:profile', kwargs={'username': 'HasNoName'})
        ]
        with freeze_time("2022-01-01 00:00:30"):
            for rev in reverses:
                response = self.client.get(rev + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)


class CacheTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_index_page_caching(self):
        with freeze_time("2022-01-01 00:00:00"):
            post = Post.objects.create(
                text='Test post',
                author=User.objects.create_user(
                    username='HasNoName'
                )
            )
            cache.clear()
            response = self.client.get(reverse('posts:index'))
            self.assertContains(response, post.text)
            post.delete()
            cache.clear()
        with freeze_time("2022-01-01 00:00:30"):
            response = self.client.get(reverse('posts:index'))
            self.assertNotContains(response, post.text)


class FollowTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='testuser@test.com',
            password='testpassword'
        )
        self.another_user = User.objects.create_user(
            username='testuser2',
            email='testuser2@test.com',
            password='testpassword2'
        )
        self.post = Post.objects.create(
            author=self.another_user,
            text='Test post text'
        )
        self.follow = Follow.objects.create(
            user=self.user,
            author=self.another_user
        )

    def test_user_can_follow_another_user(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('posts:profile_follow', args=[self.another_user.username])
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertTrue(
            Follow.objects.filter(
                user=self.user,
                author=self.another_user
            ).exists()
        )

    def test_user_can_unfollow_another_user(self):
        self.client.force_login(self.user)
        response = self.client.post(
            reverse('posts:profile_unfollow',
                    args=[self.another_user.username])
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        self.assertFalse(
            Follow.objects.filter(
                user=self.user,
                author=self.another_user
            ).exists()
        )

    def test_user_sees_posts_from_following_users_only(self):
        self.client.force_login(self.user)
        response = self.client.get(reverse('posts:follow_index'))
        self.assertContains(response, self.post.text)
        Post.objects.create(
            author=self.user,
            text='Another test post'
        )
        response = self.client.get(reverse('posts:follow_index'))
        self.assertNotContains(response, 'Another test post')

    def test_user_does_not_see_posts_from_unfollowed_users(self):
        unfollowed_user = User.objects.create_user(
            username='testuser3',
            email='testuser3@test.com',
            password='testpassword3'
        )
        post_from_unfollowed_user = Post.objects.create(
            author=unfollowed_user,
            text='Test post text from unfollowed user'
        )
        self.client.force_login(self.user)
        response = self.client.get(reverse('posts:follow_index'))
        self.assertNotContains(response, post_from_unfollowed_user.text)
