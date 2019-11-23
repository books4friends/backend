from django.test import TestCase

import json

from apps.frontend.tests.utils import AuthMixin
from apps.accounts.models import Account
from apps.books.models import Book

VK_ID = 'VK_ID'
ELSE_VK_ID = 'ELSE_VK_ID'
TITLE = 'Ходячий замок'
OLD_COMMENT = 'OLD_COMMENT'
NEW_COMMENT = 'NEW_COMMENT'


class ActivateBookItemViewTest(TestCase, AuthMixin):
    def setUp(self):
        self.account = Account.objects.create(vk_id=VK_ID)
        self.else_account = Account.objects.create(vk_id=ELSE_VK_ID)
        self.book = Book.objects.create(
            account=self.account,
            title=TITLE,
        )

    def test_activate_correct(self):
        self.auth_user(self.account)
        self.book.status = Book.STATUS.NOT_ACTIVE
        self.book.save()
        response = self.client.post('/app/api/my-books/{}/activate/'.format(self.book.id))
        self.book = Book.objects.get(id=self.book.id)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True, 'book_id': self.book.id})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.book.status, Book.STATUS.ACTIVE)

    def test_activate_activated(self):
        self.auth_user(self.account)
        self.book.status = Book.STATUS.ACTIVE
        self.book.save()
        response = self.client.post('/app/api/my-books/{}/activate/'.format(self.book.id))
        self.assertEquals(response.status_code, 404)
        self.assertEquals(self.book.status, Book.STATUS.ACTIVE)

    def test_activate_deleted(self):
        self.auth_user(self.account)
        self.book.status = Book.STATUS.DELETED
        self.book.save()
        response = self.client.post('/app/api/my-books/{}/activate/'.format(self.book.id))
        self.assertEquals(response.status_code, 404)
        self.book = Book.objects.get(id=self.book.id)
        self.assertEquals(self.book.status, Book.STATUS.DELETED)

    def test_someone_else_book(self):
        self.auth_user(self.else_account)
        self.book.status = Book.STATUS.NOT_ACTIVE
        self.book.save()
        response = self.client.post('/app/api/my-books/{}/activate/'.format(self.book.id))
        self.assertEquals(response.status_code, 404)
        self.book = Book.objects.get(id=self.book.id)
        self.assertEquals(self.book.status, Book.STATUS.NOT_ACTIVE)


class DeactivateBookItemViewTest(TestCase, AuthMixin):
    def setUp(self):
        self.account = Account.objects.create(vk_id=VK_ID)
        self.else_account = Account.objects.create(vk_id=ELSE_VK_ID)
        self.book = Book.objects.create(
            account=self.account,
            title=TITLE
        )

    def test_activate_correct(self):
        self.auth_user(self.account)
        self.book.status = Book.STATUS.ACTIVE
        self.book.save()
        response = self.client.post('/app/api/my-books/{}/deactivate/'.format(self.book.id))
        self.book = Book.objects.get(id=self.book.id)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True, 'book_id': self.book.id})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.book.status, Book.STATUS.NOT_ACTIVE)

    def test_activate_deactivated(self):
        self.auth_user(self.account)
        self.book.status = Book.STATUS.NOT_ACTIVE
        self.book.save()
        response = self.client.post('/app/api/my-books/{}/deactivate/'.format(self.book.id))
        self.assertEquals(response.status_code, 404)
        self.book = Book.objects.get(id=self.book.id)
        self.assertEquals(self.book.status, Book.STATUS.NOT_ACTIVE)

    def test_activate_deleted(self):
        self.auth_user(self.account)
        self.book.status = Book.STATUS.DELETED
        self.book.save()
        response = self.client.post('/app/api/my-books/{}/deactivate/'.format(self.book.id))
        self.assertEquals(response.status_code, 404)
        self.book = Book.objects.get(id=self.book.id)
        self.assertEquals(self.book.status, Book.STATUS.DELETED)

    def test_someone_else_book(self):
        self.auth_user(self.else_account)
        self.book.status = Book.STATUS.ACTIVE
        self.book.save()
        response = self.client.post('/app/api/my-books/{}/deactivate/'.format(self.book.id))
        self.assertEquals(response.status_code, 404)
        self.book = Book.objects.get(id=self.book.id)
        self.assertEquals(self.book.status, Book.STATUS.ACTIVE)


class DeleteBookViewTest(TestCase, AuthMixin):
    def setUp(self):
        self.account = Account.objects.create(vk_id=VK_ID)
        self.else_account = Account.objects.create(vk_id=ELSE_VK_ID)
        self.book = Book.objects.create(
            account=self.account,
            title=TITLE
        )

    def test_delete_active_correct(self):
        self.auth_user(self.account)
        self.book.status = Book.STATUS.ACTIVE
        self.book.save()
        response = self.client.post('/app/api/my-books/{}/delete/'.format(self.book.id))
        self.book = Book.objects.get(id=self.book.id)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True, 'book_id': self.book.id})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.book.status, Book.STATUS.DELETED)

    def test_delete_deactivated_correct(self):
        self.auth_user(self.account)
        self.book.status = Book.STATUS.NOT_ACTIVE
        self.book.save()
        response = self.client.post('/app/api/my-books/{}/delete/'.format(self.book.id))
        self.book = Book.objects.get(id=self.book.id)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True, 'book_id': self.book.id})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.book.status, Book.STATUS.DELETED)

    def test_activate_deleted(self):
        self.auth_user(self.account)
        self.book.status = Book.STATUS.DELETED
        self.book.save()
        response = self.client.post('/app/api/my-books/{}/delete/'.format(self.book.id))
        self.assertEquals(response.status_code, 404)
        self.book = Book.objects.get(id=self.book.id)
        self.assertEquals(self.book.status, Book.STATUS.DELETED)

    def test_someone_else_book(self):
        self.auth_user(self.else_account)
        self.book.status = Book.STATUS.ACTIVE
        self.book.save()
        response = self.client.post('/app/api/my-books/{}/delete/'.format(self.book.id))
        self.assertEquals(response.status_code, 404)
        self.book = Book.objects.get(id=self.book.id)
        self.assertEquals(self.book.status, Book.STATUS.ACTIVE)


class EditBookItemCommentViewTest(TestCase, AuthMixin):
    def setUp(self):
        self.account = Account.objects.create(vk_id=VK_ID)
        self.else_account = Account.objects.create(vk_id=ELSE_VK_ID)
        self.book = Book.objects.create(
            account=self.account,
            title=TITLE,
            comment=OLD_COMMENT
        )

    def test_edit_comment_active_correct(self):
        self.auth_user(self.account)
        self.book.status = Book.STATUS.ACTIVE
        self.book.save()
        response = self.client.post(
            '/app/api/my-books/{}/edit-comment/'.format(self.book.id),
            json.dumps({'comment': NEW_COMMENT}),
            content_type="application/json"
        )
        self.book = Book.objects.get(id=self.book.id)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True, 'book_id': self.book.id})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.book.comment, NEW_COMMENT)

    def test_edit_comment_deactivated_correct(self):
        self.auth_user(self.account)
        self.book.status = Book.STATUS.NOT_ACTIVE
        self.book.save()
        response = self.client.post(
            '/app/api/my-books/{}/edit-comment/'.format(self.book.id),
            json.dumps({'comment': NEW_COMMENT}),
            content_type="application/json"
        )
        self.book = Book.objects.get(id=self.book.id)
        self.assertJSONEqual(response.content.decode("utf-8"), {"success": True, 'book_id': self.book.id})
        self.assertEquals(response.status_code, 200)
        self.assertEquals(self.book.comment, NEW_COMMENT)

    def test_edit_comment_deleted(self):
        self.auth_user(self.account)
        self.book.status = Book.STATUS.DELETED
        self.book.save()
        response = self.client.post(
            '/app/api/my-books/{}/edit-comment/'.format(self.book.id),
            json.dumps({'comment': NEW_COMMENT}),
            content_type="application/json"
        )
        self.assertEquals(response.status_code, 404)
        self.book = Book.objects.get(id=self.book.id)
        self.assertEquals(self.book.comment, OLD_COMMENT)

    def test_someone_else_book(self):
        self.auth_user(self.else_account)
        self.book.status = Book.STATUS.ACTIVE
        self.book.save()
        response = self.client.post(
            '/app/api/my-books/{}/edit-comment/'.format(self.book.id),
            json.dumps({'comment': NEW_COMMENT}),
            content_type="application/json"
        )
        self.assertEquals(response.status_code, 404)
        self.book = Book.objects.get(id=self.book.id)
        self.assertEquals(self.book.comment, OLD_COMMENT)
