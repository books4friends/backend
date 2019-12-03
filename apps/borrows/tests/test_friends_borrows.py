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
        self.account_friend_2 = Account.objects.create(vk_id=VK_FRIEND_2['external_id'])
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
            real_return_date=CURRENT_DATE,
        )

    @mock.patch('apps.borrows.views.get_users_info', side_effect=None, return_value=[VK_FRIEND, VK_FRIEND_2])
    def test_one_borrow(self, _):
        self.auth_user(self.account_owner)
        response = self.client.get('/api/app/borrows/friends/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode('utf-8'),
            {
                "borrows": [{
                    'id': self.borrow.id,
                    'friend': {
                        'external_id': VK_FRIEND['external_id'],
                        'name': VK_FRIEND['name'],
                        'image': VK_FRIEND['image'],
                        'city': VK_FRIEND['city'],
                    },
                    "book": {
                        "id": str(self.book.id),
                        "description": {
                            "title": TITLE, "author": AUTHOR, "description": DESCRIPTION, "genre": GENRE,
                            "image": GOOGLE_IMAGE_URL,
                        },
                        "comment": '',
                        "active": True,
                    },
                    "borrow_data": {
                        "take_date": CURRENT_DATE.strftime("%Y-%m-%d"),
                        "planned_return_date": TWO_WEEKS_AFTER.strftime("%Y-%m-%d"),
                        "real_return_date": CURRENT_DATE.strftime("%Y-%m-%d"),
                    }
                }]
            })

    @mock.patch('apps.borrows.views.get_users_info', side_effect=None, return_value=[VK_FRIEND, VK_FRIEND_2])
    def test_not_friend_borrow(self, _):
        self.auth_user(self.account_not_friend)
        response = self.client.get('/api/app/borrows/friends/')
        self.assertEqual(response.status_code, 200)

        self.assertJSONEqual(
            response.content.decode('utf-8'),
            {
                "borrows": []
            })

    @mock.patch('apps.borrows.views.get_users_info', side_effect=None, return_value=[VK_FRIEND, VK_FRIEND_2])
    def test_two_borrows(self, _):
        self.auth_user(self.account_owner)

        book2 = Book.objects.create(
            account=self.account_owner,
            title=TITLE,
        )
        borrow2 = Borrow.objects.create(
            borrower=self.account_friend_2,
            book=book2,
            planned_return_date=TWO_WEEKS_AFTER,
            real_return_date=CURRENT_DATE,
        )

        response = self.client.get('/api/app/borrows/friends/')
        self.assertEqual(response.status_code, 200)

        self.assertJSONEqual(
            response.content.decode('utf-8'),
            {
                "borrows": [{
                    'id': borrow2.id,
                    'friend': {
                        'external_id': VK_FRIEND_2['external_id'],
                        'name': VK_FRIEND_2['name'],
                        'image': VK_FRIEND_2['image'],
                        'city': VK_FRIEND_2['city'],
                    },
                    "book": {
                        "id": str(book2.id),
                        "description": {
                            "title": TITLE, "author": None, "description": "", "genre": None,
                            "image": None,
                        },
                        "comment": '',
                        "active": True,
                    },
                    "borrow_data": {
                        "take_date": CURRENT_DATE.strftime("%Y-%m-%d"),
                        "planned_return_date": TWO_WEEKS_AFTER.strftime("%Y-%m-%d"),
                        "real_return_date": CURRENT_DATE.strftime("%Y-%m-%d"),
                    }
                }, {
                    'id': self.borrow.id,
                    'friend': {
                        'external_id': VK_FRIEND['external_id'],
                        'name': VK_FRIEND['name'],
                        'image': VK_FRIEND['image'],
                        'city': VK_FRIEND['city'],
                    },
                    "book": {
                        "id": str(self.book.id),
                        "description": {
                            "title": TITLE, "author": AUTHOR, "description": DESCRIPTION, "genre": GENRE,
                            "image": GOOGLE_IMAGE_URL,
                        },
                        "comment": '',
                        "active": True,
                    },
                    "borrow_data": {
                        "take_date": CURRENT_DATE.strftime("%Y-%m-%d"),
                        "planned_return_date": TWO_WEEKS_AFTER.strftime("%Y-%m-%d"),
                        "real_return_date": CURRENT_DATE.strftime("%Y-%m-%d"),
                    }
                }]
            })
