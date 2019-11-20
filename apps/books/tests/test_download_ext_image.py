from django.test import TestCase

import tempfile
from django.test import override_settings

from ..models import BookItem, BookDetail
from apps.accounts.models import Account
from ..tasks import download_external_image

VK_ID = 'VK_ID'

GOOGLE_TITLE = 'Чернильная кровь'
GOOGLE_AUTHOR = 'Корнелия Функе'
GOOGLE_BOOK_ID = 'C3hWAgAAQBAJ'
GOOGLE_IMAGE_URL = 'http://books.google.com/books/content?id=C3hWAgAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl'


class DownloadExternalImageText(TestCase):
    def setUp(self):
        self.account = Account.objects.create(vk_id=VK_ID)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_download_correct(self):
        detail = BookDetail.objects.create(
            title=GOOGLE_TITLE,
            author=GOOGLE_AUTHOR,
            external_id=GOOGLE_BOOK_ID,
        )
        self.book = BookItem.objects.create(
            account=self.account,
            detail=detail,
            image_external_url=GOOGLE_IMAGE_URL
        )

        pk = self.book.pk
        download_external_image.apply(args=(pk, )).get()

        updated_book = BookItem.objects.get(pk=pk)
        self.assertIn('book_g_' + str(pk), updated_book.image.name)

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_download_correct_no_google_id(self):
        detail = BookDetail.objects.create(
            title=GOOGLE_TITLE,
            author=GOOGLE_AUTHOR,
        )
        self.book = BookItem.objects.create(
            account=self.account,
            detail=detail,
            image_external_url=GOOGLE_IMAGE_URL
        )
        pk = self.book.pk
        download_external_image.apply(args=(pk, )).get()

        updated_book = BookItem.objects.get(pk=pk)
        self.assertIn('book_g_' + str(pk), updated_book.image.name)
