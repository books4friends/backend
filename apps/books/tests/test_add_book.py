from django.test import TestCase

import os
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from apps.frontend.tests.utils import AuthMixin
from apps.accounts.models import Account
from apps.books.models import BookDetail, BookItem

VK_ID = 'VK_ID'
TITLE = 'Ходячий замок'
AUTHOR = 'Диана Уинн Джонс'
COMMENT = 'Могу подарить'
IMAGE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/custom_image.jpg')
GOOGLE_TITLE = 'Чернильная кровь'
GOOGLE_AUTHOR = 'Корнелия Функе'
GOOGLE_BOOK_ID = 'C3hWAgAAQBAJ'
GOOGLE_IMAGE_URL = 'http://books.google.com/books/content?id=C3hWAgAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl'
GOOGLE_FAKE_BOOK_ID = 'C3hWAgA4QBAP'


class AddBookViewTest(TestCase, AuthMixin):
    def setUp(self):
        account = Account.objects.create(vk_id=VK_ID)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_adding_with_full_correct_data_and_custom_image(self):
        account = Account.objects.get(vk_id=VK_ID)
        self.auth_user(account)

        custom_image = SimpleUploadedFile(
            name='test_image.jpg', content=open(IMAGE_PATH, 'rb').read(), content_type='image/jpeg')
        response = self.client.post('/app/api/my-books/add/', {
            'title': TITLE,
            'author': AUTHOR,
            'comment': COMMENT,
            'image': custom_image
        })
        self.assertEqual(account.bookitem_set.all().count(), 1)
        book_item = account.bookitem_set.all()[0]

        self.assertEqual(book_item.detail.title, TITLE)
        self.assertEqual(book_item.detail.author, AUTHOR)
        self.assertEqual(book_item.detail.source, BookDetail.SOURCE.CUSTOM)
        self.assertIn('book_' + str(book_item.detail.id), book_item.image.name)
        self.assertEqual(book_item.comment, COMMENT)
        self.assertEqual(book_item.status, BookItem.STATUS.ACTIVE)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "success": True,
                "book": {
                    "id": str(book_item.id),
                    "description": {"title": TITLE, "author": AUTHOR, "image": book_item.image.url},
                    "comment": COMMENT,
                    "active": True
                }
            }
        )

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_adding_with_full_correct_data_and_custom_image_no_comment(self):
        account = Account.objects.get(vk_id=VK_ID)
        self.auth_user(account)

        custom_image = SimpleUploadedFile(
            name='test_image.jpg', content=open(IMAGE_PATH, 'rb').read(), content_type='image/jpeg')
        response = self.client.post('/app/api/my-books/add/', {
            'title': TITLE,
            'author': AUTHOR,
            'image': custom_image
        })
        self.assertEqual(account.bookitem_set.all().count(), 1)
        book_item = account.bookitem_set.all()[0]

        self.assertEqual(book_item.detail.title, TITLE)
        self.assertEqual(book_item.detail.author, AUTHOR)
        self.assertEqual(book_item.detail.source, BookDetail.SOURCE.CUSTOM)
        self.assertIn('book_' + str(book_item.id), book_item.image.name)
        self.assertEqual(book_item.comment, '')
        self.assertEqual(book_item.status, BookItem.STATUS.ACTIVE)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "success": True,
                "book": {
                    "id": str(book_item.id),
                    "description": {"title": TITLE, "author": AUTHOR, "image": book_item.image.url},
                    "comment": "",
                    "active": True
                }
            }
        )

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_adding_with_full_correct_data_and_custom_image_no_author(self):
        account = Account.objects.get(vk_id=VK_ID)
        self.auth_user(account)

        custom_image = SimpleUploadedFile(
            name='test_image.jpg', content=open(IMAGE_PATH, 'rb').read(), content_type='image/jpeg')
        response = self.client.post('/app/api/my-books/add/', {
            'title': TITLE,
            'comment': COMMENT,
            'image': custom_image
        })
        self.assertEqual(account.bookitem_set.all().count(), 1)
        book_item = account.bookitem_set.all()[0]

        self.assertEqual(book_item.detail.title, TITLE)
        self.assertEqual(book_item.detail.author, '')
        self.assertEqual(book_item.detail.source, BookDetail.SOURCE.CUSTOM)
        self.assertIn('book_' + str(book_item.detail.id), book_item.image.name)
        self.assertEqual(book_item.comment, COMMENT)
        self.assertEqual(book_item.status, BookItem.STATUS.ACTIVE)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "success": True,
                "book": {
                    "id": str(book_item.id),
                    "description": {"title": TITLE, "author": "", "image": book_item.image.url},
                    "comment": COMMENT,
                    "active": True
                }
            }
        )

    def test_no_data(self):
        account = Account.objects.get(vk_id=VK_ID)
        self.auth_user(account)
        response = self.client.post('/app/api/my-books/add/', {})

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "success": False,
                "error_type": "FORM_NOT_VALID",
                "errors": {"title": ["This field is required."]}
            }
        )

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_adding_with_google_correct(self):
        account = Account.objects.get(vk_id=VK_ID)
        self.auth_user(account)

        response = self.client.post('/app/api/my-books/add/', {
            'title': GOOGLE_TITLE,
            'author': GOOGLE_AUTHOR,
            'external_id': GOOGLE_BOOK_ID,
            'external_image': GOOGLE_IMAGE_URL,
            'comment': COMMENT,
        })
        self.assertEqual(account.bookitem_set.all().count(), 1)
        book_item = account.bookitem_set.all()[0]

        self.assertEqual(book_item.detail.title, GOOGLE_TITLE)
        self.assertEqual(book_item.detail.author, GOOGLE_AUTHOR)
        self.assertEqual(book_item.detail.source, BookDetail.SOURCE.GOOGLE)
        self.assertIn(GOOGLE_IMAGE_URL, book_item.image_external_url)
        self.assertEqual(book_item.comment, COMMENT)
        self.assertEqual(book_item.status, BookItem.STATUS.ACTIVE)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "success": True,
                "book": {
                    "id": str(book_item.id),
                    "description": {
                        "title": GOOGLE_TITLE,
                        "author": GOOGLE_AUTHOR,
                        "image": book_item.image_external_url
                    },
                    "comment": COMMENT,
                    "active": True
                }
            }
        )

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_adding_with_external_image(self):
        account = Account.objects.get(vk_id=VK_ID)
        self.auth_user(account)

        response = self.client.post('/app/api/my-books/add/', {
            'title': GOOGLE_TITLE,
            'author': GOOGLE_AUTHOR,
            'external_image': GOOGLE_IMAGE_URL,
            'comment': COMMENT,
        })
        self.assertEqual(account.bookitem_set.all().count(), 1)
        book_item = account.bookitem_set.all()[0]

        self.assertEqual(book_item.detail.title, GOOGLE_TITLE)
        self.assertEqual(book_item.detail.author, GOOGLE_AUTHOR)
        self.assertEqual(book_item.detail.source, BookDetail.SOURCE.CUSTOM)
        self.assertIn(GOOGLE_IMAGE_URL, book_item.image_external_url)
        self.assertEqual(book_item.comment, COMMENT)
        self.assertEqual(book_item.status, BookItem.STATUS.ACTIVE)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "success": True,
                "book": {
                    "id": str(book_item.id),
                    "description": {
                        "title": GOOGLE_TITLE,
                        "author": GOOGLE_AUTHOR,
                        "image": book_item.image_external_url
                    },
                    "comment": COMMENT,
                    "active": True
                }
            }
        )