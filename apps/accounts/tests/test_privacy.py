from django.test import TestCase

import json
from unittest import mock

from apps.frontend.tests.utils import AuthMixin
from apps.accounts.models import Account, FriendsWhiteList, FriendsBlackList
from apps.vk_service.tests.utils import generate_vk_users

VK_ID = 'VK_ID'
ELSE_VK_ID = 'ELSE_VK_ID'
VK_FRIEND, VK_FRIEND_2, VK_FRIEND_3, VK_FRIEND_4 = generate_vk_users(4)


class PrivacyFriendsListViewTest(TestCase, AuthMixin):
    def setUp(self):
        self.account = Account.objects.create(vk_id=VK_ID)

    @mock.patch('apps.accounts.views.update_privacy_settings_view.get_friends_list', side_effect=None, return_value=[])
    def test_url(self, _):
        self.auth_user(self.account)
        response = self.client.get('/app/api/settings/privacy/friends/')
        self.assertEqual(response.status_code, 200)

    @mock.patch('apps.accounts.views.update_privacy_settings_view.get_friends_list', side_effect=None,
                return_value=[])
    def test_zero_friends(self, _):
        self.auth_user(self.account)
        response = self.client.get('/app/api/settings/privacy/friends/')
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {"success": True, "friends": []}
        )

    @mock.patch('apps.accounts.views.update_privacy_settings_view.get_friends_list', side_effect=None,
                return_value=[VK_FRIEND])
    def test_just_friend(self, _):
        self.auth_user(self.account)
        response = self.client.get('/app/api/settings/privacy/friends/')
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {"success": True, "friends": [{
                'external_id': VK_FRIEND['external_id'],
                'name': VK_FRIEND['name'],
                'image': VK_FRIEND['image'],
                'city': VK_FRIEND['city'],
                'whitelist_selected': False,
                'blacklist_selected': False,
            }]}
        )

    @mock.patch('apps.accounts.views.update_privacy_settings_view.get_friends_list', side_effect=None,
                return_value=[VK_FRIEND])
    def test_friend_in_whitelist(self, _):
        self.auth_user(self.account)
        FriendsWhiteList.objects.create(owner=self.account, friend_ext_id=VK_FRIEND['external_id'])
        response = self.client.get('/app/api/settings/privacy/friends/')
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {"success": True, "friends": [{
                'external_id': VK_FRIEND['external_id'],
                'name': VK_FRIEND['name'],
                'image': VK_FRIEND['image'],
                'city': VK_FRIEND['city'],
                'whitelist_selected': True,
                'blacklist_selected': False,
            }]}
        )

    @mock.patch('apps.accounts.views.update_privacy_settings_view.get_friends_list', side_effect=None,
                return_value=[VK_FRIEND])
    def test_friend_in_blacklist(self, _):
        self.auth_user(self.account)
        FriendsBlackList.objects.create(owner=self.account, friend_ext_id=VK_FRIEND['external_id'])
        response = self.client.get('/app/api/settings/privacy/friends/')
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {"success": True, "friends": [{
                'external_id': VK_FRIEND['external_id'],
                'name': VK_FRIEND['name'],
                'image': VK_FRIEND['image'],
                'city': VK_FRIEND['city'],
                'whitelist_selected': False,
                'blacklist_selected': True,
            }]}
        )

    @mock.patch('apps.accounts.views.update_privacy_settings_view.get_friends_list', side_effect=None,
                return_value=[VK_FRIEND, VK_FRIEND_2, VK_FRIEND_3, VK_FRIEND_4])
    def test_complex(self, _):
        self.auth_user(self.account)
        FriendsWhiteList.objects.create(owner=self.account, friend_ext_id=VK_FRIEND_2['external_id'])
        FriendsWhiteList.objects.create(owner=self.account, friend_ext_id=VK_FRIEND_3['external_id'])
        FriendsBlackList.objects.create(owner=self.account, friend_ext_id=VK_FRIEND_3['external_id'])
        FriendsBlackList.objects.create(owner=self.account, friend_ext_id=VK_FRIEND_4['external_id'])
        response = self.client.get('/app/api/settings/privacy/friends/')
        response_json = json.loads(response.content)['friends'],
        response_json = response_json[0]

        self.assertEquals(len(response_json), 4)
        self.assertEquals(
            response_json[0], {
                'external_id': VK_FRIEND['external_id'],
                'name': VK_FRIEND['name'],
                'image': VK_FRIEND['image'],
                'city': VK_FRIEND['city'],
                'whitelist_selected': False,
                'blacklist_selected': False,
            }
        )
        self.assertEquals(
            response_json[1], {
                'external_id': VK_FRIEND_2['external_id'],
                'name': VK_FRIEND_2['name'],
                'image': VK_FRIEND_2['image'],
                'city': VK_FRIEND_2['city'],
                'whitelist_selected': True,
                'blacklist_selected': False,
            }
        )
        self.assertEquals(
            response_json[2], {
                'external_id': VK_FRIEND_3['external_id'],
                'name': VK_FRIEND_3['name'],
                'image': VK_FRIEND_3['image'],
                'city': VK_FRIEND_3['city'],
                'whitelist_selected': True,
                'blacklist_selected': True,
            }
        )
        self.assertEquals(
            response_json[3], {
                'external_id': VK_FRIEND_4['external_id'],
                'name': VK_FRIEND_4['name'],
                'image': VK_FRIEND_4['image'],
                'city': VK_FRIEND_4['city'],
                'whitelist_selected': False,
                'blacklist_selected': True,
            }
        )

    @mock.patch('apps.accounts.views.update_privacy_settings_view.get_friends_list', side_effect=None,
                return_value=[])
    def test_else_account(self, _):
        else_account = Account.objects.create(vk_id=ELSE_VK_ID)
        self.auth_user(else_account)
        FriendsBlackList.objects.create(owner=self.account, friend_ext_id=VK_FRIEND['external_id'])
        response = self.client.get('/app/api/settings/privacy/friends/')
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {"success": True, "friends": []}
        )

    @mock.patch('apps.accounts.views.update_privacy_settings_view.get_friends_list', side_effect=None,
                return_value=[VK_FRIEND])
    def test_not_actual_data(self, _):
        self.auth_user(self.account)
        FriendsBlackList.objects.create(owner=self.account, friend_ext_id=VK_FRIEND_2['external_id'])
        response = self.client.get('/app/api/settings/privacy/friends/')
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {"success": True, "friends": [{
                'external_id': VK_FRIEND['external_id'],
                'name': VK_FRIEND['name'],
                'image': VK_FRIEND['image'],
                'city': VK_FRIEND['city'],
                'whitelist_selected': False,
                'blacklist_selected': False,
            }]}
        )


class SetPrivacyAllFriendsViewTest(TestCase, AuthMixin):
    def setUp(self):
        self.account = Account.objects.create(vk_id=VK_ID)

    def test_correct(self):
        self.auth_user(self.account)
        self.account.privacy_type = Account.PRIVACY_TYPE.EXCEPT_SOME_FRIENDS
        self.account.save()
        response = self.client.post('/app/api/settings/privacy/set-all-friends/')
        self.assertEqual(response.status_code, 200)
        account = Account.objects.get(vk_id=VK_ID)
        self.assertEqual(account.privacy_type, Account.PRIVACY_TYPE.ALL_FRIENDS)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True})

    def test_no_change(self):
        self.auth_user(self.account)
        self.account.privacy_type = Account.PRIVACY_TYPE.ALL_FRIENDS
        self.account.save()
        response = self.client.post('/app/api/settings/privacy/set-all-friends/')
        self.assertEqual(response.status_code, 200)
        account = Account.objects.get(vk_id=VK_ID)
        self.assertEqual(account.privacy_type, Account.PRIVACY_TYPE.ALL_FRIENDS)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True})

    def test_whitelists_not_changed(self):
        self.auth_user(self.account)
        self.account.privacy_type = Account.PRIVACY_TYPE.ONLY_SOME_FRIENDS
        self.account.save()
        FriendsWhiteList.objects.create(owner=self.account, friend_ext_id=VK_FRIEND_2['external_id'])
        FriendsWhiteList.objects.create(owner=self.account, friend_ext_id=VK_FRIEND_3['external_id'])

        response = self.client.post('/app/api/settings/privacy/set-all-friends/')
        account = Account.objects.get(vk_id=VK_ID)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True})
        self.assertEqual(account.privacy_type, Account.PRIVACY_TYPE.ALL_FRIENDS)
        self.assertEqual(account.friendswhitelist_set.all().count(), 2)

    def test_blacklists_not_changed(self):
        self.auth_user(self.account)
        self.account.privacy_type = Account.PRIVACY_TYPE.EXCEPT_SOME_FRIENDS
        self.account.save()
        FriendsBlackList.objects.create(owner=self.account, friend_ext_id=VK_FRIEND_2['external_id'])
        FriendsBlackList.objects.create(owner=self.account, friend_ext_id=VK_FRIEND_3['external_id'])

        response = self.client.post('/app/api/settings/privacy/set-all-friends/')
        account = Account.objects.get(vk_id=VK_ID)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True})
        self.assertEqual(account.privacy_type, Account.PRIVACY_TYPE.ALL_FRIENDS)
        self.assertEqual(account.friendsblacklist_set.all().count(), 2)

    def test_else_account(self):
        self.auth_user(self.account)
        self.account.privacy_type = Account.PRIVACY_TYPE.ONLY_OWNER
        self.account.save()
        else_account = Account.objects.create(vk_id=ELSE_VK_ID)
        else_account.privacy_type = Account.PRIVACY_TYPE.ONLY_OWNER
        else_account.save()

        response = self.client.post('/app/api/settings/privacy/set-all-friends/')
        self.assertEqual(response.status_code, 200)
        account = Account.objects.get(vk_id=VK_ID)
        self.assertEqual(account.privacy_type, Account.PRIVACY_TYPE.ALL_FRIENDS)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True})
        else_account = Account.objects.get(vk_id=ELSE_VK_ID)
        self.assertEqual(else_account.privacy_type, Account.PRIVACY_TYPE.ONLY_OWNER)


class SetPrivacyOnlyOwnerViewTest(TestCase, AuthMixin):
    def setUp(self):
        self.account = Account.objects.create(vk_id=VK_ID)

    def test_correct(self):
        self.auth_user(self.account)
        self.account.privacy_type = Account.PRIVACY_TYPE.EXCEPT_SOME_FRIENDS
        self.account.save()
        response = self.client.post('/app/api/settings/privacy/set-only-owner/')
        self.assertEqual(response.status_code, 200)
        account = Account.objects.get(vk_id=VK_ID)
        self.assertEqual(account.privacy_type, Account.PRIVACY_TYPE.ONLY_OWNER)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True})

    def test_no_change(self):
        self.auth_user(self.account)
        self.account.privacy_type = Account.PRIVACY_TYPE.ONLY_OWNER
        self.account.save()
        response = self.client.post('/app/api/settings/privacy/set-only-owner/')
        self.assertEqual(response.status_code, 200)
        account = Account.objects.get(vk_id=VK_ID)
        self.assertEqual(account.privacy_type, Account.PRIVACY_TYPE.ONLY_OWNER)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True})

    def test_whitelists_not_changed(self):
        self.auth_user(self.account)
        self.account.privacy_type = Account.PRIVACY_TYPE.ONLY_SOME_FRIENDS
        self.account.save()
        FriendsWhiteList.objects.create(owner=self.account, friend_ext_id=VK_FRIEND_2['external_id'])
        FriendsWhiteList.objects.create(owner=self.account, friend_ext_id=VK_FRIEND_3['external_id'])

        response = self.client.post('/app/api/settings/privacy/set-only-owner/')
        account = Account.objects.get(vk_id=VK_ID)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True})
        self.assertEqual(account.privacy_type, Account.PRIVACY_TYPE.ONLY_OWNER)
        self.assertEqual(account.friendswhitelist_set.all().count(), 2)

    def test_blacklists_not_changed(self):
        self.auth_user(self.account)
        self.account.privacy_type = Account.PRIVACY_TYPE.EXCEPT_SOME_FRIENDS
        self.account.save()
        FriendsBlackList.objects.create(owner=self.account, friend_ext_id=VK_FRIEND_2['external_id'])
        FriendsBlackList.objects.create(owner=self.account, friend_ext_id=VK_FRIEND_3['external_id'])

        response = self.client.post('/app/api/settings/privacy/set-only-owner/')
        account = Account.objects.get(vk_id=VK_ID)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True})
        self.assertEqual(account.privacy_type, Account.PRIVACY_TYPE.ONLY_OWNER)
        self.assertEqual(account.friendsblacklist_set.all().count(), 2)

    def test_else_account(self):
        self.auth_user(self.account)
        self.account.privacy_type = Account.PRIVACY_TYPE.ALL_FRIENDS
        self.account.save()
        else_account = Account.objects.create(vk_id=ELSE_VK_ID)
        else_account.privacy_type = Account.PRIVACY_TYPE.ALL_FRIENDS
        else_account.save()

        response = self.client.post('/app/api/settings/privacy/set-only-owner/')
        self.assertEqual(response.status_code, 200)
        account = Account.objects.get(vk_id=VK_ID)
        self.assertEqual(account.privacy_type, Account.PRIVACY_TYPE.ONLY_OWNER)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True})
        else_account = Account.objects.get(vk_id=ELSE_VK_ID)
        self.assertEqual(else_account.privacy_type, Account.PRIVACY_TYPE.ALL_FRIENDS)


class SetPrivacySomeFriendsViewTest(TestCase, AuthMixin):
    def setUp(self):
        self.account = Account.objects.create(vk_id=VK_ID)

    def test_correct(self):
        self.auth_user(self.account)
        self.account.privacy_type = Account.PRIVACY_TYPE.ALL_FRIENDS
        self.account.save()
        response = self.client.post(
            '/app/api/settings/privacy/set-some-friends/',
            json.dumps({'selected_friends': [VK_FRIEND_2['external_id'], VK_FRIEND_3['external_id']]}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        account = Account.objects.get(vk_id=VK_ID)
        self.assertEqual(account.privacy_type, Account.PRIVACY_TYPE.ONLY_SOME_FRIENDS)
        self.assertEqual(account.friendswhitelist_set.all().count(), 2)
        self.assertTrue(account.friendswhitelist_set.filter(friend_ext_id=VK_FRIEND_2['external_id']).exists())
        self.assertTrue(account.friendswhitelist_set.filter(friend_ext_id=VK_FRIEND_3['external_id']).exists())
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True})

    def test_change_list(self):
        self.auth_user(self.account)
        self.account.privacy_type = Account.PRIVACY_TYPE.ONLY_SOME_FRIENDS
        FriendsWhiteList.objects.create(owner=self.account, friend_ext_id=VK_FRIEND['external_id'])
        FriendsWhiteList.objects.create(owner=self.account, friend_ext_id=VK_FRIEND_2['external_id'])
        FriendsWhiteList.objects.create(owner=self.account, friend_ext_id=VK_FRIEND_3['external_id'])
        self.account.save()
        response = self.client.post(
            '/app/api/settings/privacy/set-some-friends/',
            json.dumps({'selected_friends': [VK_FRIEND_3['external_id'], VK_FRIEND_4['external_id']]}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        account = Account.objects.get(vk_id=VK_ID)
        self.assertEqual(account.privacy_type, Account.PRIVACY_TYPE.ONLY_SOME_FRIENDS)
        self.assertEqual(account.friendswhitelist_set.all().count(), 2)
        self.assertTrue(account.friendswhitelist_set.filter(friend_ext_id=VK_FRIEND_3['external_id']).exists())
        self.assertTrue(account.friendswhitelist_set.filter(friend_ext_id=VK_FRIEND_4['external_id']).exists())
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True})

    def test_blacklists_not_changed(self):
        self.auth_user(self.account)
        self.account.privacy_type = Account.PRIVACY_TYPE.EXCEPT_SOME_FRIENDS
        self.account.save()
        FriendsBlackList.objects.create(owner=self.account, friend_ext_id=VK_FRIEND_2['external_id'])
        FriendsBlackList.objects.create(owner=self.account, friend_ext_id=VK_FRIEND_3['external_id'])

        response = self.client.post(
            '/app/api/settings/privacy/set-some-friends/',
            json.dumps({'selected_friends': [VK_FRIEND_3['external_id'], VK_FRIEND_4['external_id']]}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True})
        account = Account.objects.get(vk_id=VK_ID)

        self.assertEqual(account.privacy_type, Account.PRIVACY_TYPE.ONLY_SOME_FRIENDS)
        self.assertEqual(account.friendswhitelist_set.all().count(), 2)
        self.assertTrue(account.friendswhitelist_set.filter(friend_ext_id=VK_FRIEND_3['external_id']).exists())
        self.assertTrue(account.friendswhitelist_set.filter(friend_ext_id=VK_FRIEND_4['external_id']).exists())

        self.assertEqual(account.friendsblacklist_set.all().count(), 2)
        self.assertTrue(account.friendsblacklist_set.filter(friend_ext_id=VK_FRIEND_2['external_id']).exists())
        self.assertTrue(account.friendsblacklist_set.filter(friend_ext_id=VK_FRIEND_3['external_id']).exists())

    def test_else_account(self):
        self.auth_user(self.account)
        self.account.privacy_type = Account.PRIVACY_TYPE.ONLY_OWNER
        self.account.save()
        else_account = Account.objects.create(vk_id=ELSE_VK_ID)
        else_account.privacy_type = Account.PRIVACY_TYPE.ONLY_OWNER
        else_account.save()

        response = self.client.post(
            '/app/api/settings/privacy/set-some-friends/',
            json.dumps({'selected_friends': [VK_FRIEND_2['external_id'], VK_FRIEND_3['external_id']]}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        account = Account.objects.get(vk_id=VK_ID)
        self.assertEqual(account.privacy_type, Account.PRIVACY_TYPE.ONLY_SOME_FRIENDS)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True})
        else_account = Account.objects.get(vk_id=ELSE_VK_ID)
        self.assertEqual(else_account.privacy_type, Account.PRIVACY_TYPE.ONLY_OWNER)


class SetPrivacyExceptSomeFriendsViewTest(TestCase, AuthMixin):
    def setUp(self):
        self.account = Account.objects.create(vk_id=VK_ID)

    def test_correct(self):
        self.auth_user(self.account)
        self.account.privacy_type = Account.PRIVACY_TYPE.ALL_FRIENDS
        self.account.save()
        response = self.client.post(
            '/app/api/settings/privacy/set-except-some-friends/',
            json.dumps({'selected_friends': [VK_FRIEND_2['external_id'], VK_FRIEND_3['external_id']]}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        account = Account.objects.get(vk_id=VK_ID)
        self.assertEqual(account.privacy_type, Account.PRIVACY_TYPE.EXCEPT_SOME_FRIENDS)
        self.assertEqual(account.friendsblacklist_set.all().count(), 2)
        self.assertTrue(account.friendsblacklist_set.filter(friend_ext_id=VK_FRIEND_2['external_id']).exists())
        self.assertTrue(account.friendsblacklist_set.filter(friend_ext_id=VK_FRIEND_3['external_id']).exists())
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True})

    def test_change_list(self):
        self.auth_user(self.account)
        self.account.privacy_type = Account.PRIVACY_TYPE.ONLY_SOME_FRIENDS
        FriendsBlackList.objects.create(owner=self.account, friend_ext_id=VK_FRIEND['external_id'])
        FriendsBlackList.objects.create(owner=self.account, friend_ext_id=VK_FRIEND_2['external_id'])
        FriendsBlackList.objects.create(owner=self.account, friend_ext_id=VK_FRIEND_3['external_id'])
        self.account.save()
        response = self.client.post(
            '/app/api/settings/privacy/set-except-some-friends/',
            json.dumps({'selected_friends': [VK_FRIEND_3['external_id'], VK_FRIEND_4['external_id']]}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        account = Account.objects.get(vk_id=VK_ID)
        self.assertEqual(account.privacy_type, Account.PRIVACY_TYPE.EXCEPT_SOME_FRIENDS)
        self.assertEqual(account.friendsblacklist_set.all().count(), 2)
        self.assertTrue(account.friendsblacklist_set.filter(friend_ext_id=VK_FRIEND_3['external_id']).exists())
        self.assertTrue(account.friendsblacklist_set.filter(friend_ext_id=VK_FRIEND_4['external_id']).exists())
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True})

    def test_whitelists_not_changed(self):
        self.auth_user(self.account)
        self.account.privacy_type = Account.PRIVACY_TYPE.ONLY_SOME_FRIENDS
        self.account.save()
        FriendsWhiteList.objects.create(owner=self.account, friend_ext_id=VK_FRIEND_2['external_id'])
        FriendsWhiteList.objects.create(owner=self.account, friend_ext_id=VK_FRIEND_3['external_id'])

        response = self.client.post(
            '/app/api/settings/privacy/set-except-some-friends/',
            json.dumps({'selected_friends': [VK_FRIEND_3['external_id'], VK_FRIEND_4['external_id']]}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True})
        account = Account.objects.get(vk_id=VK_ID)

        self.assertEqual(account.privacy_type, Account.PRIVACY_TYPE.EXCEPT_SOME_FRIENDS)
        self.assertEqual(account.friendsblacklist_set.all().count(), 2)
        self.assertTrue(account.friendsblacklist_set.filter(friend_ext_id=VK_FRIEND_3['external_id']).exists())
        self.assertTrue(account.friendsblacklist_set.filter(friend_ext_id=VK_FRIEND_4['external_id']).exists())

        self.assertEqual(account.friendswhitelist_set.all().count(), 2)
        self.assertTrue(account.friendswhitelist_set.filter(friend_ext_id=VK_FRIEND_2['external_id']).exists())
        self.assertTrue(account.friendswhitelist_set.filter(friend_ext_id=VK_FRIEND_3['external_id']).exists())

    def test_else_account(self):
        self.auth_user(self.account)
        self.account.privacy_type = Account.PRIVACY_TYPE.ONLY_OWNER
        self.account.save()
        else_account = Account.objects.create(vk_id=ELSE_VK_ID)
        else_account.privacy_type = Account.PRIVACY_TYPE.ONLY_OWNER
        else_account.save()

        response = self.client.post(
            '/app/api/settings/privacy/set-except-some-friends/',
            json.dumps({'selected_friends': [VK_FRIEND_2['external_id'], VK_FRIEND_3['external_id']]}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        account = Account.objects.get(vk_id=VK_ID)
        self.assertEqual(account.privacy_type, Account.PRIVACY_TYPE.EXCEPT_SOME_FRIENDS)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True})
        else_account = Account.objects.get(vk_id=ELSE_VK_ID)
        self.assertEqual(else_account.privacy_type, Account.PRIVACY_TYPE.ONLY_OWNER)


