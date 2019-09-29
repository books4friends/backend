from django.test import TestCase

import os
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.frontend.tests.utils import AuthMixin
from apps.accounts.models import Account
from apps.books.models import BookDetail, BookItem

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
        book_item = self.book_item = BookItem.objects.create(
            detail=BookDetail.objects.create(title=TITLE, author=AUTHOR, image=custom_image),
            account=self.account
        )

        self.auth_user(self.account)
        response = self.client.get('/app/api/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": [{
                    "id": str(book_item.id),
                    "description": {"title": TITLE, "author": AUTHOR, "image": book_item.detail.image.url},
                    "comment": '',
                    "active": True
                }]
            }
        )

    def test_google_book(self):
        custom_image = SimpleUploadedFile(
            name='test_image.jpg', content=open(IMAGE_PATH, 'rb').read(), content_type='image/jpeg')
        book_item = self.book_item = BookItem.objects.create(
            detail=BookDetail.objects.create(title=TITLE, author=AUTHOR, image=custom_image,
                                             source=BookDetail.SOURCE.GOOGLE, image_external_url=GOOGLE_IMAGE_URL),
            account=self.account
        )

        self.auth_user(self.account)
        response = self.client.get('/app/api/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": [{
                    "id": str(book_item.id),
                    "description": {"title": TITLE, "author": AUTHOR, "image": book_item.detail.image.url},
                    "comment": '',
                    "active": True
                }]
            }
        )

    def test_google_book_with_not_downloaded_image(self):
        book_item = self.book_item = BookItem.objects.create(
            detail=BookDetail.objects.create(title=TITLE, author=AUTHOR, source=BookDetail.SOURCE.GOOGLE,
                                             image_external_url=GOOGLE_IMAGE_URL),
            account=self.account
        )

        self.auth_user(self.account)
        response = self.client.get('/app/api/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": [{
                    "id": str(book_item.id),
                    "description": {"title": TITLE, "author": AUTHOR, "image": GOOGLE_IMAGE_URL},
                    "comment": '',
                    "active": True
                }]
            }
        )

    def test_book_with_no_comment(self):
        book_item = self.book_item = BookItem.objects.create(
            detail=BookDetail.objects.create(title=TITLE, author=AUTHOR),
            account=self.account
        )

        self.auth_user(self.account)
        response = self.client.get('/app/api/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": [{
                    "id": str(book_item.id),
                    "description": {"title": TITLE, "author": AUTHOR, "image": None},
                    "comment": '',
                    "active": True
                }]
            }
        )

    def test_book_with_comment(self):
        book_item = self.book_item = BookItem.objects.create(
            detail=BookDetail.objects.create(title=TITLE, author=AUTHOR),
            account=self.account,
            comment=COMMENT
        )

        self.auth_user(self.account)
        response = self.client.get('/app/api/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": [{
                    "id": str(book_item.id),
                    "description": {"title": TITLE, "author": AUTHOR, "image": None},
                    "comment": COMMENT,
                    "active": True
                }]
            }
        )

    def test_book_with_author(self):
        book_item = self.book_item = BookItem.objects.create(
            detail=BookDetail.objects.create(title=TITLE, author=AUTHOR),
            account=self.account,
        )

        self.auth_user(self.account)
        response = self.client.get('/app/api/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": [{
                    "id": str(book_item.id),
                    "description": {"title": TITLE, "author": AUTHOR, "image": None},
                    "comment": "",
                    "active": True
                }]
            }
        )

    def test_book_without_author(self):
        book_item = self.book_item = BookItem.objects.create(
            detail=BookDetail.objects.create(title=TITLE),
            account=self.account,
        )

        self.auth_user(self.account)
        response = self.client.get('/app/api/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": [{
                    "id": str(book_item.id),
                    "description": {"title": TITLE, "author": None, "image": None},
                    "comment": "",
                    "active": True
                }]
            }
        )

    def test_deactivated(self):
        book_item = self.book_item = BookItem.objects.create(
            detail=BookDetail.objects.create(title=TITLE, author=AUTHOR),
            account=self.account,
            status=BookItem.STATUS.NOT_ACTIVE
        )

        self.auth_user(self.account)
        response = self.client.get('/app/api/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": [{
                    "id": str(book_item.id),
                    "description": {"title": TITLE, "author": AUTHOR, "image": None},
                    "comment": "",
                    "active": False
                }]
            }
        )

    def test_deleted(self):
        book_item = self.book_item = BookItem.objects.create(
            detail=BookDetail.objects.create(title=TITLE, author=AUTHOR),
            account=self.account,
            status=BookItem.STATUS.DELETED
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
        book_item = self.book_item = BookItem.objects.create(
            detail=BookDetail.objects.create(title=TITLE, author=AUTHOR),
            account=self.account,
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
        book_item1 = self.book_item = BookItem.objects.create(
            detail=BookDetail.objects.create(title=TITLE, author=AUTHOR),
            account=self.account,
        )
        book_item2 = self.book_item = BookItem.objects.create(
            detail=BookDetail.objects.create(title=TITLE_2, author=AUTHOR_2),
            account=self.account,
            status=BookItem.STATUS.NOT_ACTIVE
        )
        book_item3 = self.book_item = BookItem.objects.create(
            detail=BookDetail.objects.create(title=TITLE_3, author=AUTHOR_3),
            account=self.account,
            status=BookItem.STATUS.DELETED
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
