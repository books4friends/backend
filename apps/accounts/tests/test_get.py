from django.test import TestCase

from apps.frontend.tests.utils import AuthMixin
from apps.accounts.models import Account

VK_ID = 'VK_ID'


class AccountSettingsViewTest(TestCase, AuthMixin):
    def setUp(self):
        self.account = Account.objects.create(vk_id=VK_ID)

    def test_url_exists_at_desired_location(self):
        self.auth_user(self.account)
        response = self.client.get('/api/app/settings/')
        self.assertEqual(response.status_code, 200)

    def test_default_privacy(self):
        self.auth_user(self.account)
        response = self.client.get('/api/app/settings/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {'privacy_type': Account.PRIVACY_TYPE.ALL_FRIENDS}
        )

    def test_only_owner_privacy(self):
        self.auth_user(self.account)
        self.account.privacy_type = Account.PRIVACY_TYPE.ONLY_OWNER
        self.account.save()
        response = self.client.get('/api/app/settings/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {'privacy_type': Account.PRIVACY_TYPE.ONLY_OWNER}
        )


