from django.test import TestCase

import json

from apps.frontend.tests.utils import AuthMixin
from apps.accounts.models import Account
from apps.books.models import BookDetail, BookItem

VK_ID = 'VK_ID'
ELSE_VK_ID = 'ELSE_VK_ID'
TITLE = 'Ходячий замок'
OLD_COMMENT = 'OLD_COMMENT'
NEW_COMMENT = 'NEW_COMMENT'


class ActivateBookItemViewTest(TestCase, AuthMixin):
    def setUp(self):
        self.account = Account.objects.create(vk_id=VK_ID)
        self.else_account = Account.objects.create(vk_id=ELSE_VK_ID)
        self.book_detail = BookDetail.objects.create(title=TITLE)
        self.book_item = BookItem.objects.create(
            detail=self.book_detail,
            account=self.account,
        )

    def test_activate_correct(self):
        self.auth_user(self.account)
        self.book_item.status = BookItem.STATUS.NOT_ACTIVE
        self.book_item.save()
        response = self.client.post('/app/api/my-books/{}/activate/'.format(self.book_item.id))
        self.book_item = BookItem.objects.get(id=self.book_item.id)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True, 'book_id': self.book_item.id})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.book_item.status, BookItem.STATUS.ACTIVE)

    def test_activate_activated(self):
        self.auth_user(self.account)
        self.book_item.status = BookItem.STATUS.ACTIVE
        self.book_item.save()
        response = self.client.post('/app/api/my-books/{}/activate/'.format(self.book_item.id))
        self.assertEquals(response.status_code, 404)
        self.assertEquals(self.book_item.status, BookItem.STATUS.ACTIVE)

    def test_activate_deleted(self):
        self.auth_user(self.account)
        self.book_item.status = BookItem.STATUS.DELETED
        self.book_item.save()
        response = self.client.post('/app/api/my-books/{}/activate/'.format(self.book_item.id))
        self.assertEquals(response.status_code, 404)
        self.book_item = BookItem.objects.get(id=self.book_item.id)
        self.assertEquals(self.book_item.status, BookItem.STATUS.DELETED)

    def test_someone_else_book(self):
        self.auth_user(self.else_account)
        self.book_item.status = BookItem.STATUS.NOT_ACTIVE
        self.book_item.save()
        response = self.client.post('/app/api/my-books/{}/activate/'.format(self.book_item.id))
        self.assertEquals(response.status_code, 404)
        self.book_item = BookItem.objects.get(id=self.book_item.id)
        self.assertEquals(self.book_item.status, BookItem.STATUS.NOT_ACTIVE)


class DeactivateBookItemViewTest(TestCase, AuthMixin):
    def setUp(self):
        self.account = Account.objects.create(vk_id=VK_ID)
        self.else_account = Account.objects.create(vk_id=ELSE_VK_ID)
        self.book_detail = BookDetail.objects.create(title=TITLE)
        self.book_item = BookItem.objects.create(
            detail=self.book_detail,
            account=self.account,
        )

    def test_activate_correct(self):
        self.auth_user(self.account)
        self.book_item.status = BookItem.STATUS.ACTIVE
        self.book_item.save()
        response = self.client.post('/app/api/my-books/{}/deactivate/'.format(self.book_item.id))
        self.book_item = BookItem.objects.get(id=self.book_item.id)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True, 'book_id': self.book_item.id})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.book_item.status, BookItem.STATUS.NOT_ACTIVE)

    def test_activate_deactivated(self):
        self.auth_user(self.account)
        self.book_item.status = BookItem.STATUS.NOT_ACTIVE
        self.book_item.save()
        response = self.client.post('/app/api/my-books/{}/deactivate/'.format(self.book_item.id))
        self.assertEquals(response.status_code, 404)
        self.book_item = BookItem.objects.get(id=self.book_item.id)
        self.assertEquals(self.book_item.status, BookItem.STATUS.NOT_ACTIVE)

    def test_activate_deleted(self):
        self.auth_user(self.account)
        self.book_item.status = BookItem.STATUS.DELETED
        self.book_item.save()
        response = self.client.post('/app/api/my-books/{}/deactivate/'.format(self.book_item.id))
        self.assertEquals(response.status_code, 404)
        self.book_item = BookItem.objects.get(id=self.book_item.id)
        self.assertEquals(self.book_item.status, BookItem.STATUS.DELETED)

    def test_someone_else_book(self):
        self.auth_user(self.else_account)
        self.book_item.status = BookItem.STATUS.ACTIVE
        self.book_item.save()
        response = self.client.post('/app/api/my-books/{}/deactivate/'.format(self.book_item.id))
        self.assertEquals(response.status_code, 404)
        self.book_item = BookItem.objects.get(id=self.book_item.id)
        self.assertEquals(self.book_item.status, BookItem.STATUS.ACTIVE)


class DeleteBookViewTest(TestCase, AuthMixin):
    def setUp(self):
        self.account = Account.objects.create(vk_id=VK_ID)
        self.else_account = Account.objects.create(vk_id=ELSE_VK_ID)
        self.book_detail = BookDetail.objects.create(title=TITLE)
        self.book_item = BookItem.objects.create(
            detail=self.book_detail,
            account=self.account,
        )

    def test_delete_active_correct(self):
        self.auth_user(self.account)
        self.book_item.status = BookItem.STATUS.ACTIVE
        self.book_item.save()
        response = self.client.post('/app/api/my-books/{}/delete/'.format(self.book_item.id))
        self.book_item = BookItem.objects.get(id=self.book_item.id)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True, 'book_id': self.book_item.id})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.book_item.status, BookItem.STATUS.DELETED)

    def test_delete_deactivated_correct(self):
        self.auth_user(self.account)
        self.book_item.status = BookItem.STATUS.NOT_ACTIVE
        self.book_item.save()
        response = self.client.post('/app/api/my-books/{}/delete/'.format(self.book_item.id))
        self.book_item = BookItem.objects.get(id=self.book_item.id)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True, 'book_id': self.book_item.id})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.book_item.status, BookItem.STATUS.DELETED)

    def test_activate_deleted(self):
        self.auth_user(self.account)
        self.book_item.status = BookItem.STATUS.DELETED
        self.book_item.save()
        response = self.client.post('/app/api/my-books/{}/delete/'.format(self.book_item.id))
        self.assertEquals(response.status_code, 404)
        self.book_item = BookItem.objects.get(id=self.book_item.id)
        self.assertEquals(self.book_item.status, BookItem.STATUS.DELETED)

    def test_someone_else_book(self):
        self.auth_user(self.else_account)
        self.book_item.status = BookItem.STATUS.ACTIVE
        self.book_item.save()
        response = self.client.post('/app/api/my-books/{}/delete/'.format(self.book_item.id))
        self.assertEquals(response.status_code, 404)
        self.book_item = BookItem.objects.get(id=self.book_item.id)
        self.assertEquals(self.book_item.status, BookItem.STATUS.ACTIVE)


class EditBookItemCommentViewTest(TestCase, AuthMixin):
    def setUp(self):
        self.account = Account.objects.create(vk_id=VK_ID)
        self.else_account = Account.objects.create(vk_id=ELSE_VK_ID)
        self.book_detail = BookDetail.objects.create(title=TITLE)
        self.book_item = BookItem.objects.create(
            detail=self.book_detail,
            account=self.account,
            comment=OLD_COMMENT
        )

    def test_edit_comment_active_correct(self):
        self.auth_user(self.account)
        self.book_item.status = BookItem.STATUS.ACTIVE
        self.book_item.save()
        response = self.client.post(
            '/app/api/my-books/{}/edit-comment/'.format(self.book_item.id),
            json.dumps({'comment': NEW_COMMENT}),
            content_type="application/json"
        )
        self.book_item = BookItem.objects.get(id=self.book_item.id)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True, 'book_id': self.book_item.id})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.book_item.comment, NEW_COMMENT)

    def test_edit_comment_deactivated_correct(self):
        self.auth_user(self.account)
        self.book_item.status = BookItem.STATUS.NOT_ACTIVE
        self.book_item.save()
        response = self.client.post(
            '/app/api/my-books/{}/edit-comment/'.format(self.book_item.id),
            json.dumps({'comment': NEW_COMMENT}),
            content_type="application/json"
        )
        self.book_item = BookItem.objects.get(id=self.book_item.id)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True, 'book_id': self.book_item.id})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.book_item.comment, NEW_COMMENT)

    def test_edit_comment_deleted(self):
        self.auth_user(self.account)
        self.book_item.status = BookItem.STATUS.DELETED
        self.book_item.save()
        response = self.client.post(
            '/app/api/my-books/{}/edit-comment/'.format(self.book_item.id),
            json.dumps({'comment': NEW_COMMENT}),
            content_type="application/json"
        )
        self.assertEquals(response.status_code, 404)
        self.book_item = BookItem.objects.get(id=self.book_item.id)
        self.assertEquals(self.book_item.comment, OLD_COMMENT)

    def test_someone_else_book(self):
        self.auth_user(self.else_account)
        self.book_item.status = BookItem.STATUS.ACTIVE
        self.book_item.save()
        response = self.client.post(
            '/app/api/my-books/{}/edit-comment/'.format(self.book_item.id),
            json.dumps({'comment': NEW_COMMENT}),
            content_type="application/json"
        )
        self.assertEquals(response.status_code, 404)
        self.book_item = BookItem.objects.get(id=self.book_item.id)
        self.assertEquals(self.book_item.comment, OLD_COMMENT)
