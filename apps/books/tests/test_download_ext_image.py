from django.test import TestCase

import tempfile
from django.test import override_settings

from ..models import Book
from apps.accounts.models import Account
from ..tasks import download_external_image

VK_ID = 'VK_ID'
ELSE_VK_ID = 'ELSE_VK_ID'

GOOGLE_TITLE = 'Чернильная кровь'
GOOGLE_AUTHOR = 'Корнелия Функе'
GOOGLE_BOOK_ID = 'C3hWAgAAQBAJ'
GOOGLE_IMAGE_URL = 'http://books.google.com/books/content?id=C3hWAgAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl'

GOOGLE_TITLE_2 = 'Стамбул'
GOOGLE_AUTHOR_2 = 'Орхан Памук'
GOOGLE_IMAGE_URL_2 = 'http://books.google.com/books/content?id=-vFTBgAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl&source=gbs_api'


class DownloadExternalImageText(TestCase):
    def setUp(self):
        self.account = Account.objects.create(vk_id=VK_ID)
        self.account2 = Account.objects.create(vk_id=ELSE_VK_ID)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_download_correct(self):
        book = Book.objects.create(
            account=self.account,
            title=GOOGLE_TITLE,
            author=GOOGLE_AUTHOR,
            external_id=GOOGLE_BOOK_ID,
            image_external_url=GOOGLE_IMAGE_URL
        )

        pk = book.pk
        download_external_image.apply(args=(pk, )).get()

        updated_book = Book.objects.get(pk=pk)
        self.assertIn('book_g_' + str(pk), updated_book.image.name)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_download_correct_no_google_id(self):
        book = Book.objects.create(
            account=self.account,
            title=GOOGLE_TITLE,
            author=GOOGLE_AUTHOR,
            image_external_url=GOOGLE_IMAGE_URL
        )
        pk = book.pk
        download_external_image.apply(args=(pk, )).get()

        updated_book = Book.objects.get(pk=pk)
        self.assertIn('book_g_' + str(pk), updated_book.image.name)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_download_existing(self):
        book1 = Book.objects.create(
            account=self.account,
            title=GOOGLE_TITLE,
            author=GOOGLE_AUTHOR,
            image_external_url=GOOGLE_IMAGE_URL
        )
        download_external_image.apply(args=(book1.pk, )).get()
        book1 = Book.objects.get(pk=book1.pk)

        book2 = Book.objects.create(
            account=self.account2,
            title=GOOGLE_TITLE,
            author=GOOGLE_AUTHOR,
            image_external_url=GOOGLE_IMAGE_URL
        )
        download_external_image.apply(args=(book2.pk, )).get()
        book2 = Book.objects.get(pk=book2.pk)

        self.assertEqual(book1.image.name, book2.image.name)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_download_different(self):
        book1 = Book.objects.create(
            account=self.account,
            title=GOOGLE_TITLE,
            author=GOOGLE_AUTHOR,
            image_external_url=GOOGLE_IMAGE_URL
        )
        download_external_image.apply(args=(book1.pk,)).get()
        book1 = Book.objects.get(pk=book1.pk)
        book2 = Book.objects.create(
            account=self.account2,
            title=GOOGLE_TITLE_2,
            author=GOOGLE_AUTHOR_2,
            image_external_url=GOOGLE_IMAGE_URL_2
        )
        download_external_image.apply(args=(book2.pk,)).get()
        book2 = Book.objects.get(pk=book2.pk)

        self.assertNotEqual(book1.image.name, book2.image.name)
