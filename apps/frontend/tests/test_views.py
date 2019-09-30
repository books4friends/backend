from django.test import TestCase

from unittest import mock
import datetime

from apps.accounts.models import Account
from .utils import AuthMixin, get_expires_at, EXPIRES_IN

VK_ID = 'VK_ID'
ACCESS_TOKEN = 'ACCESS_TOKEN'


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

    def test_secondary_urls_exist_at_desired_location(self):
        self.auth_user(account=Account.objects.get(vk_id=VK_ID))
        response = self.client.get('/app/my-books/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/app/settings/')
        self.assertEqual(response.status_code, 200)
        response = self.client.get('/app/about/')
        self.assertEqual(response.status_code, 200)

    def test_react_loaded(self):
        self.auth_user(account=Account.objects.get(vk_id=VK_ID))
        response = self.client.get('/app/')
        self.assertContains(response, '<script type="text/javascript" src="/static/frontend/app/app.js"></script>')

    def test_secondary_urls_react_loaded(self):
        self.auth_user(account=Account.objects.get(vk_id=VK_ID))
        response = self.client.get('/app/my-books/')
        self.assertContains(response, '<script type="text/javascript" src="/static/frontend/app/app.js"></script>')
        response = self.client.get('/app/settings/')
        self.assertContains(response, '<script type="text/javascript" src="/static/frontend/app/app.js"></script>')
        response = self.client.get('/app/about/')
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


class VkRedirectViewTest(TestCase, AuthMixin):
    login_data = {
            'access_token': ACCESS_TOKEN,
            'expires_in': EXPIRES_IN,
            'user_id': VK_ID
        }

    def setUp(self):
        account = Account.objects.create(vk_id=VK_ID)

    def test_url_exists_at_desired_location(self):
        response = self.client.get('/vk_redirect_uri/')
        self.assertEqual(response.status_code, 200)

    @mock.patch('apps.frontend.views.check_token', side_effect=None, return_value=True)
    def test_redirect_with_correct_data(self, mock_auth):
        response = self.client.post('/vk_redirect_uri/', data=self.login_data)
        self.assertRedirects(response, '/app/')

    @mock.patch('apps.frontend.views.check_token', side_effect=None, return_value=False)
    def test_error_with_false_data(self, mock_auth):
        response = self.client.post('/vk_redirect_uri/', data=self.login_data)
        self.assertEqual(response.status_code, 401)

    @mock.patch('apps.frontend.views.check_token', side_effect=None, return_value=True)
    def test_session_with_correct_data(self, mock_auth):
        self.client.post('/vk_redirect_uri/', data=self.login_data)
        session = self.client.session
        account = Account.objects.get(vk_id=VK_ID)
        vk_session = account.vksession_set.all().order_by('-id')[0]
        self.assertEqual(session['vk_session_id'], vk_session.id)
        self.assertEqual(session['access_token'], ACCESS_TOKEN)
        self.assertEqual(session['account_id'], account.id)
        self.assertEqual(session['vk_id'], VK_ID)

    @mock.patch('apps.frontend.views.check_token', side_effect=None, return_value=False)
    def test_session_with_false_data(self, mock_auth):
        self.client.post('/vk_redirect_uri/', data=self.login_data)
        session = self.client.session
        self.assertFalse('vk_session_id' in session)
        self.assertFalse('access_token' in session)
        self.assertFalse('account_id' in session)
        self.assertFalse('vk_id' in session)

    @mock.patch('apps.frontend.views.check_token', side_effect=None, return_value=True)
    def test_vk_session_with_correct_data(self, mock_auth):
        self.client.post('/vk_redirect_uri/', data=self.login_data)
        account = Account.objects.get(vk_id=VK_ID)
        vk_session = account.vksession_set.all().order_by('-id')[0]
        self.assertEqual(vk_session.access_token, ACCESS_TOKEN)
        self.assertAlmostEqual(vk_session.expires_at, get_expires_at(), delta=datetime.timedelta(seconds=1))

    def test_post_redirect_authenticated(self):
        self.auth_user(account=Account.objects.get(vk_id=VK_ID))
        response = self.client.post('/vk_redirect_uri/', data=self.login_data)
        self.assertRedirects(response, '/app/')

    def test_get_redirect_authenticated(self):
        self.auth_user(account=Account.objects.get(vk_id=VK_ID))
        response = self.client.get('/vk_redirect_uri/')
        self.assertRedirects(response, '/app/')


class LogoutViewTest(TestCase, AuthMixin):

    def setUp(self):
        account = Account.objects.create(vk_id=VK_ID)

    def test_url_exists_at_desired_location(self):
        self.auth_user(account=Account.objects.get(vk_id=VK_ID))
        response = self.client.post('/logout/')
        self.assertEqual(response.status_code, 200)

    def test_url_not_get_request(self):
        self.auth_user(account=Account.objects.get(vk_id=VK_ID))
        response = self.client.get('/logout/')
        self.assertEqual(response.status_code, 405)

    def test_session_authenticated(self):
        self.auth_user(account=Account.objects.get(vk_id=VK_ID))
        self.client.post('/logout/')
        session = self.client.session
        self.assertFalse('vk_session_id' in session)
        self.assertFalse('access_token' in session)
        self.assertFalse('account_id' in session)
        self.assertFalse('vk_id' in session)

    def test_session_not_authenticated(self):
        self.client.post('/logout/')
        session = self.client.session
        self.assertFalse('vk_session_id' in session)
        self.assertFalse('access_token' in session)
        self.assertFalse('account_id' in session)
        self.assertFalse('vk_id' in session)
