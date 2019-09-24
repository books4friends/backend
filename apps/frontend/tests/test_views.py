from django.test import TestCase

from apps.accounts.models import Account
from .utils import AuthMixin

VK_ID = 'testId'


class RootViewTest(TestCase, AuthMixin):
    def setUp(self):
        account = Account.objects.create(vk_id=VK_ID)

    def test_url_exists_at_desired_location(self):
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)

    def test_redirect_authenticated(self):
        self.auth_user(account=Account.objects.get(vk_id=VK_ID))
        response = self.client.get('/')
        self.assertRedirects(response, '/app/')


class AppViewTest(TestCase, AuthMixin):
    def setUp(self):
        account = Account.objects.create(vk_id=VK_ID)

    def test_url_exists_at_desired_location(self):
        self.auth_user(account=Account.objects.get(vk_id=VK_ID))
        response = self.client.get('/app/')
        self.assertEqual(response.status_code, 200)

    def test_react_loaded(self):
        self.auth_user(account=Account.objects.get(vk_id=VK_ID))
        response = self.client.get('/app/')
        self.assertContains(response, '<script type="text/javascript" src="/static/frontend/app/app.js"></script>')

    def test_redirect_not_authenticated(self):
        response = self.client.get('/app/')
        self.assertRedirects(response, '/')

    def test_russian_language(self):
        account = Account.objects.get(vk_id=VK_ID)
        self.auth_user(account=account)
        account.locale = Account.LOCALE.RU
        account.save()
        response = self.client.get('/app/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '"locale": "ru"')

    def test_undefined_language(self):
        account = Account.objects.get(vk_id=VK_ID)
        self.auth_user(account=account)
        response = self.client.get('/app/')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, '"locale": "undefined"')
