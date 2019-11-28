from django.test import TestCase

import os
from unittest import mock
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.frontend.tests.utils import AuthMixin
from apps.accounts.models import Account
from apps.books.models import Book
from apps.vk_service.tests.utils import generate_vk_users

VK_USER, VK_FRIEND = generate_vk_users(2)

TITLE = 'Ходячий замок'
AUTHOR = 'Диана Уинн Джонс'
DESCRIPTION = 'Книги английской писательницы Дианы У. Джонс настолько ярки, что так и просятся на экран. По ее бестселлеру "Ходячий замок" знаменитый мультипликатор Хаяо Миядзаки ("Унесенные призраками"), обладатель "Золотого льва" - высшей награды Венецианского фестиваля, снял анимационный фильм, побивший в Японии рекорды кассовых сборов. Софи живет в сказочной стране, где ведьмы и русалки, семимильные сапоги и говорящие собаки - обычное дело. Поэтому, когда на нее обрушивается ужасное проклятие коварной Болотной Ведьмы, Софи ничего не остается, как обратиться за помощью к таинственному чародею Хоулу, обитающему в ходячем замке. Однако, чтобы освободиться от чар, Софи предстоит разгадать немало загадок и прожить в замке у Хоула гораздо дольше, чем она рассчитывала. А для этого нужно подружиться с огненным демоном, поймать падучую звезду, подслушать пение русалок, отыскать мандрагору и многое, многое другое.'
GOOGLE_IMAGE_URL = 'http://books.google.com/books/content?id=C3hWAgAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl'


class MyBooksListViewTest(TestCase, AuthMixin):
    def setUp(self):
        self.account = Account.objects.create(vk_id=VK_USER['external_id'])
        self.account2 = Account.objects.create(vk_id=VK_FRIEND['external_id'])
        self.book = Book.objects.create(
            account=self.account,
            title=TITLE,
            author=AUTHOR,
            description=DESCRIPTION,
            image_external_url=GOOGLE_IMAGE_URL,
        )

    @mock.patch('apps.books.views.book_detail.get_user_info', side_effect=None,
                return_value=VK_USER)
    def test_url_exists_at_desired_location(self, _):
        self.auth_user(self.account)
        response = self.client.get('/api/app/book/{}/'.format(self.book.id))
        self.assertEqual(response.status_code, 200)

    @mock.patch('apps.books.views.book_detail.get_user_info', side_effect=None, return_value=VK_USER)
    def test_my_book(self, _):
        self.auth_user(self.account)
        response = self.client.get('/api/app/book/{}/'.format(self.book.id))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                'book': {
                    "id": str(self.book.id),
                    "description": {
                        "title": TITLE, "author": AUTHOR, "image": GOOGLE_IMAGE_URL, "description": DESCRIPTION
                    },
                    "comment": '',
                    "active": True
                },
                'owner_type': 'self',
                'owner': {
                    'external_id': VK_USER['external_id'],
                    'name': VK_USER['name'],
                    'image': VK_USER['image'],
                    'city': VK_USER['city'],
                }
            }
        )

    @mock.patch('apps.books.views.book_detail.get_friends_list', side_effect=None, return_value=[VK_USER])
    def test_friends_book(self, _):
        self.auth_user(self.account2)
        response = self.client.get('/api/app/book/{}/'.format(self.book.id))
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                'book': {
                    "id": str(self.book.id),
                    "description": {
                        "title": TITLE, "author": AUTHOR, "image": GOOGLE_IMAGE_URL, "description": DESCRIPTION
                    },
                    "comment": '',
                    "active": True
                },
                'owner_type': 'friend',
                'owner': {
                    'external_id': VK_USER['external_id'],
                    'name': VK_USER['name'],
                    'image': VK_USER['image'],
                    'city': VK_USER['city'],
                }
            }
        )

    @mock.patch('apps.books.views.book_detail.get_friends_list', side_effect=None, return_value=[])
    def test_else_book(self, _):
        self.auth_user(self.account2)
        response = self.client.get('/api/app/book/{}/'.format(self.book.id))
        self.assertEqual(response.status_code, 404)
