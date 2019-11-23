from django.test import TestCase

import os
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.frontend.tests.utils import AuthMixin
from apps.accounts.models import Account
from apps.books.models import Book

VK_ID = 'VK_ID'
ELSE_ACCOUNT = 'ELSE_ACCOUNT'
TITLE = 'Ходячий замок'
AUTHOR = 'Диана Уинн Джонс'
TITLE_2 = 'Мать'
AUTHOR_2 = 'Максим Горький'
TITLE_3 = 'Манюня'
AUTHOR_3 = 'Наринэ Абгарян'
COMMENT = 'Могу подарить'
IMAGE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/custom_image.jpg')
GOOGLE_TITLE = 'Чернильная кровь'
GOOGLE_AUTHOR = 'Корнелия Функе'
GOOGLE_BOOK_ID = 'C3hWAgAAQBAJ'
GOOGLE_IMAGE_URL = 'http://books.google.com/books/content?id=C3hWAgAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl'


class MyBooksListViewTest(TestCase, AuthMixin):
    def setUp(self):
        self.account = Account.objects.create(vk_id=VK_ID)

    def test_url_exists_at_desired_location(self):
        self.auth_user(self.account)
        response = self.client.get('/app/api/my-books/')
        self.assertEqual(response.status_code, 200)

    def test_custom_book(self):
        custom_image = SimpleUploadedFile(
            name='test_image.jpg', content=open(IMAGE_PATH, 'rb').read(), content_type='image/jpeg')
        book = self.book = Book.objects.create(
            account=self.account,
            title=TITLE,
            author=AUTHOR,
            image=custom_image
        )

        self.auth_user(self.account)
        response = self.client.get('/app/api/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": [{
                    "id": str(book.id),
                    "description": {"title": TITLE, "author": AUTHOR, "image": book.image.url},
                    "comment": '',
                    "active": True
                }]
            }
        )

    def test_google_book(self):
        custom_image = SimpleUploadedFile(
            name='test_image.jpg', content=open(IMAGE_PATH, 'rb').read(), content_type='image/jpeg'
        )
        book = self.book = Book.objects.create(
            account=self.account,
            image=custom_image,
            image_external_url=GOOGLE_IMAGE_URL,
            title=TITLE,
            author=AUTHOR,
            source=Book.SOURCE.GOOGLE,
        )

        self.auth_user(self.account)
        response = self.client.get('/app/api/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": [{
                    "id": str(book.id),
                    "description": {"title": TITLE, "author": AUTHOR, "image": book.image.url},
                    "comment": '',
                    "active": True
                }]
            }
        )

    def test_google_book_with_not_downloaded_image(self):
        book = self.book = Book.objects.create(
            account=self.account,
            title=TITLE,
            author=AUTHOR,
            source=Book.SOURCE.GOOGLE,
            image_external_url=GOOGLE_IMAGE_URL,
        )

        self.auth_user(self.account)
        response = self.client.get('/app/api/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": [{
                    "id": str(book.id),
                    "description": {"title": TITLE, "author": AUTHOR, "image": GOOGLE_IMAGE_URL},
                    "comment": '',
                    "active": True
                }]
            }
        )

    def test_book_with_no_comment(self):
        book = self.book = Book.objects.create(
            account=self.account,
            title=TITLE,
            author=AUTHOR,
        )

        self.auth_user(self.account)
        response = self.client.get('/app/api/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": [{
                    "id": str(book.id),
                    "description": {"title": TITLE, "author": AUTHOR, "image": None},
                    "comment": '',
                    "active": True
                }]
            }
        )

    def test_book_with_comment(self):
        book = self.book = Book.objects.create(
            account=self.account,
            title=TITLE,
            author=AUTHOR,
            comment=COMMENT
        )

        self.auth_user(self.account)
        response = self.client.get('/app/api/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": [{
                    "id": str(book.id),
                    "description": {"title": TITLE, "author": AUTHOR, "image": None},
                    "comment": COMMENT,
                    "active": True
                }]
            }
        )

    def test_book_with_author(self):
        book = self.book = Book.objects.create(
            account=self.account,
            title=TITLE,
            author=AUTHOR,
        )

        self.auth_user(self.account)
        response = self.client.get('/app/api/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": [{
                    "id": str(book.id),
                    "description": {"title": TITLE, "author": AUTHOR, "image": None},
                    "comment": "",
                    "active": True
                }]
            }
        )

    def test_book_without_author(self):
        book = self.book = Book.objects.create(
            account=self.account,
            title=TITLE
        )

        self.auth_user(self.account)
        response = self.client.get('/app/api/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": [{
                    "id": str(book.id),
                    "description": {"title": TITLE, "author": None, "image": None},
                    "comment": "",
                    "active": True
                }]
            }
        )

    def test_deactivated(self):
        book = self.book = Book.objects.create(
            account=self.account,
            title=TITLE,
            author=AUTHOR,
            status=Book.STATUS.NOT_ACTIVE
        )

        self.auth_user(self.account)
        response = self.client.get('/app/api/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": [{
                    "id": str(book.id),
                    "description": {"title": TITLE, "author": AUTHOR, "image": None},
                    "comment": "",
                    "active": False
                }]
            }
        )

    def test_deleted(self):
        book = self.book = Book.objects.create(
            account=self.account,
            title=TITLE,
            author=AUTHOR,
            status=Book.STATUS.DELETED
        )

        self.auth_user(self.account)
        response = self.client.get('/app/api/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": []
            }
        )

    def test_no_books(self):
        self.auth_user(self.account)
        response = self.client.get('/app/api/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": []
            }
        )

    def test_someone_else_book(self):
        book = self.book = Book.objects.create(
            account=self.account,
            title=TITLE,
            author=AUTHOR,
        )

        self.auth_user(Account.objects.create(vk_id=ELSE_ACCOUNT))
        response = self.client.get('/app/api/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": []
            }
        )

    def test_a_few_book_list(self):
        book_item1 = self.book = Book.objects.create(
            account=self.account,
            title=TITLE,
            author=AUTHOR,
        )
        book_item2 = self.book = Book.objects.create(
            account=self.account,
            title=TITLE_2,
            author=AUTHOR_2,
            status=Book.STATUS.NOT_ACTIVE
        )
        book_item3 = self.book = Book.objects.create(
            account=self.account,
            title=TITLE_3,
            author=AUTHOR_3,
            status=Book.STATUS.DELETED
        )

        self.auth_user(self.account)
        response = self.client.get('/app/api/my-books/')
        self.assertEqual(response.status_code, 200)

        import json

        response_json = json.loads(response.content)['books'],
        response_json = response_json[0]
        self.assertEquals(len(response_json), 2)
        self.assertEquals(
            response_json[1], {
                "id": str(book_item1.id),
                "description": {"title": TITLE, "author": AUTHOR, "image": None},
                "comment": "",
                "active": True
            }
        )
        self.assertEquals(
            response_json[0], {
                "id": str(book_item2.id),
                "description": {"title": TITLE_2, "author": AUTHOR_2, "image": None},
                "comment": "",
                "active": False
            }
        )
