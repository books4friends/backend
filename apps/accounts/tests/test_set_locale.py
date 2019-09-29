from django.test import TestCase

import json

from apps.frontend.tests.utils import AuthMixin
from apps.accounts.models import Account

VK_ID = 'VK_ID'


class AccountSettingsViewTest(TestCase, AuthMixin):
    def setUp(self):
        self.account = Account.objects.create(vk_id=VK_ID)

    def test_set_russian_locale(self):
        self.auth_user(self.account)
        response = self.client.post(
            '/app/api/settings/locale/set/',
            json.dumps({'locale': Account.LOCALE.RU}),
            content_type="application/json"
        )
        self.account = Account.objects.get(vk_id=VK_ID)
        self.assertEqual(self.account.locale, Account.LOCALE.RU)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True})

    def test_set_english_locale(self):
        self.auth_user(self.account)
        response = self.client.post(
            '/app/api/settings/locale/set/',
            json.dumps({'locale': Account.LOCALE.EN}),
            content_type="application/json"
        )
        self.account = Account.objects.get(vk_id=VK_ID)
        self.assertEqual(self.account.locale, Account.LOCALE.EN)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True})

    def test_set_from_russian_to_english_locale(self):
        self.auth_user(self.account)
        self.account.locale = Account.LOCALE.RU
        response = self.client.post(
            '/app/api/settings/locale/set/',
            json.dumps({'locale': Account.LOCALE.EN}),
            content_type="application/json"
        )
        self.account = Account.objects.get(vk_id=VK_ID)
        self.assertEqual(self.account.locale, Account.LOCALE.EN)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True})

    def test_set_wrong_locale(self):
        self.auth_user(self.account)
        response = self.client.post(
            '/app/api/settings/locale/set/',
            json.dumps({'locale': 'WL'}),
            content_type="application/json"
        )
        self.account = Account.objects.get(vk_id=VK_ID)
        self.assertEqual(self.account.locale, None)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": False})

