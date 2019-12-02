from django.test import TestCase

from unittest import mock
import json
import datetime

from apps.frontend.tests.utils import AuthMixin
from apps.vk_service.tests.utils import generate_vk_users
from apps.borrows.models import Borrow
from apps.books.models import Book
from apps.accounts.models import Account

VK_USER, VK_FRIEND,  VK_FRIEND_2, VK_NOT_FRIEND = generate_vk_users(4)
TITLE = 'Ходячий замок'


class AddBorrowViewTest(TestCase, AuthMixin):
    def setUp(self):
        self.account_owner = Account.objects.create(vk_id=VK_USER['external_id'])
        self.account_friend = Account.objects.create(vk_id=VK_FRIEND['external_id'])
        self.account_friend_2 = Account.objects.create(vk_id=VK_FRIEND_2['external_id'])
        self.account_not_friend = Account.objects.create(vk_id=VK_NOT_FRIEND['external_id'])
        self.current_date = datetime.datetime.now().date()
        self.two_weeks_after = self.current_date + datetime.timedelta(days=14)

        self.book = Book.objects.create(title=TITLE, account=self.account_owner)

    @mock.patch('apps.borrows.views.get_friends_list', side_effect=None, return_value=[VK_USER, VK_FRIEND_2])
    def test_success(self, _):
        self.auth_user(self.account_friend)
        response = self.client.post('/api/app/borrows/create/', json.dumps({
            'book_id': self.book.id,
            'planned_return_date': self.two_weeks_after.strftime("%Y-%m-%d")
        }), content_type="application/json")

        borrow = Borrow.objects.all()[0]
        self.assertEqual(borrow.book_id, self.book.id)
        self.assertEqual(borrow.planned_return_date, self.two_weeks_after)
        self.assertEqual(borrow.take_date, self.current_date)
        self.assertEqual(borrow.borrower, self.account_friend)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "success": True
            }
        )

    @mock.patch('apps.borrows.views.get_friends_list', side_effect=None, return_value=[VK_USER, VK_FRIEND_2])
    def test_old_date(self, _):
        self.auth_user(self.account_friend)
        date = self.current_date - datetime.timedelta(days=1)
        response = self.client.post('/api/app/borrows/create/', json.dumps({
            'book_id': self.book.id,
            'planned_return_date': date.strftime("%Y-%m-%d")
        }), content_type="application/json")

        self.assertEqual(0, Borrow.objects.all().count())
        self.assertEqual(response.status_code, 200)

    @mock.patch('apps.borrows.views.get_friends_list', side_effect=None, return_value=[VK_FRIEND_2])
    def test_not_friend(self, _):
        self.auth_user(self.account_not_friend)
        response = self.client.post('/api/app/borrows/create/', json.dumps({
            'book_id': self.book.id,
            'planned_return_date': self.two_weeks_after.strftime("%Y-%m-%d")
        }), content_type="application/json")

        self.assertEqual(0, Borrow.objects.all().count())
        self.assertEqual(response.status_code, 404)

    @mock.patch('apps.borrows.views.get_friends_list', side_effect=None, return_value=[VK_USER, VK_FRIEND_2])
    def test_already_taken(self, _):
        Borrow.objects.create(
            borrower=self.account_friend,
            book=self.book,
            planned_return_date=self.two_weeks_after
        )

        self.auth_user(self.account_friend_2)
        response = self.client.post('/api/app/borrows/create/', json.dumps({
            'book_id': self.book.id,
            'planned_return_date': self.two_weeks_after.strftime("%Y-%m-%d")
        }), content_type="application/json")

        self.assertEqual(1, Borrow.objects.all().count())

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "success": False,
                "error_type": "ALREADY_TAKEN",
            }
        )

    @mock.patch('apps.borrows.views.get_friends_list', side_effect=None, return_value=[VK_USER, VK_FRIEND_2])
    def test_after_return(self, _):
        Borrow.objects.create(
            borrower=self.account_friend,
            book=self.book,
            planned_return_date=self.current_date,
            real_return_date=self.current_date,
        )

        self.auth_user(self.account_friend_2)
        response = self.client.post('/api/app/borrows/create/', json.dumps({
            'book_id': self.book.id,
            'planned_return_date': self.two_weeks_after.strftime("%Y-%m-%d")
        }), content_type="application/json")

        self.assertEqual(2, Borrow.objects.all().count())

        borrow = Borrow.objects.all().order_by('-id')[0]
        self.assertEqual(borrow.book_id, self.book.id)
        self.assertEqual(borrow.planned_return_date, self.two_weeks_after)
        self.assertEqual(borrow.take_date, self.current_date)
        self.assertEqual(borrow.borrower, self.account_friend_2)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "success": True
            }
        )
