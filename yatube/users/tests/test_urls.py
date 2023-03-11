from django.contrib.auth.views import (LoginView,
                                       LogoutView,
                                       PasswordChangeDoneView,
                                       PasswordResetCompleteView,
                                       PasswordResetConfirmView,
                                       PasswordResetDoneView,
                                       PasswordResetView
                                       )
from django.test import SimpleTestCase
from django.urls import resolve, reverse
from users.views import SignUp, PasswordChange


class TestUrls(SimpleTestCase):
    def test_logout_url_resolves(self):
        url = reverse('users:logout')
        self.assertEqual(resolve(url).func.view_class, LogoutView)

    def test_signup_url_resolves(self):
        url = reverse('users:signup')
        self.assertEqual(resolve(url).func.view_class, SignUp)

    def test_login_url_resolves(self):
        url = reverse('users:login')
        self.assertEqual(resolve(url).func.view_class, LoginView)

    def test_password_change_url_resolves(self):
        url = reverse('users:password_change')
        self.assertEqual(resolve(url).func.view_class, PasswordChange)

    def test_password_change_done_url_resolves(self):
        url = reverse('users:password_change_done')
        self.assertEqual(resolve(url).func.view_class, PasswordChangeDoneView)

    def test_password_reset_form_url_resolves(self):
        url = reverse('users:password_reset_form')
        self.assertEqual(resolve(url).func.view_class, PasswordResetView)

    def test_password_reset_done_url_resolves(self):
        url = reverse('users:password_reset_done')
        self.assertEqual(resolve(url).func.view_class, PasswordResetDoneView)

    def test_password_reset_confirm_url_resolves(self):
        url = reverse('users:password_reset_confirm', args=['uidb64', 'token'])
        self.assertEqual(
            resolve(url).func.view_class, PasswordResetConfirmView
        )

    def test_password_reset_complete_url_resolves(self):
        url = reverse('users:password_reset_complete')
        self.assertEqual(
            resolve(url).func.view_class, PasswordResetCompleteView
        )
