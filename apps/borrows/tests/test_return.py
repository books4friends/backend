from django.test import TestCase

import datetime

from apps.frontend.tests.utils import AuthMixin
from apps.vk_service.tests.utils import generate_vk_users
from apps.borrows.models import Borrow
from apps.books.models import Book
from apps.accounts.models import Account

VK_USER, VK_FRIEND, VK_NOT_FRIEND = generate_vk_users(3)
TITLE = 'Ходячий замок'
AUTHOR = 'Диана Уинн Джонс'
DESCRIPTION = 'Книги английской писательницы Дианы У. Джонс'
GOOGLE_IMAGE_URL = 'http://books.google.com/books/content?id=C3hWAgAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl'
GENRE = 9

CURRENT_DATE = datetime.datetime.now().date()
TWO_WEEKS_AFTER = CURRENT_DATE + datetime.timedelta(days=14)


class MyBorrowsListViewTest(TestCase, AuthMixin):
    def setUp(self):
        self.account_owner = Account.objects.create(vk_id=VK_USER['external_id'])
        self.account_friend = Account.objects.create(vk_id=VK_FRIEND['external_id'])
        self.account_not_friend = Account.objects.create(vk_id=VK_NOT_FRIEND['external_id'])

        self.book = Book.objects.create(
            account=self.account_owner,
            title=TITLE,
            author=AUTHOR,
            description=DESCRIPTION,
            genre=GENRE,
            image_external_url=GOOGLE_IMAGE_URL,
        )
        self.borrow = Borrow.objects.create(
            borrower=self.account_friend,
            book=self.book,
            planned_return_date=TWO_WEEKS_AFTER,
        )

    def return_success(self):
        self.auth_user(self.account_friend)
        response = self.client.post('/api/app/borrows/{}/return/'.format(self.borrow.pk))
        self.assertEqual(self.borrow.real_return_date, CURRENT_DATE)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {"success": True}
        )

    def return_returned(self):
        self.auth_user(self.account_friend)
        yesterday = CURRENT_DATE - datetime.timedelta(days=1)
        self.borrow.real_return_date = yesterday
        self.borrow.save()
        response = self.client.post('/api/app/borrows/{}/return/'.format(self.borrow.pk))
        self.assertEqual(self.borrow.real_return_date, yesterday)
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {"success": False, 'error_type': 'ALREADY_RETURNED'}
        )

    def return_else(self):
        self.auth_user(self.account_not_friend)
        response = self.client.post('/api/app/borrows/{}/return/'.format(self.borrow.pk))
        self.assertEqual(response.status_code, 404)
