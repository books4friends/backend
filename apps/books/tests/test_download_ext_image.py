from django.test import TestCase

import tempfile
from django.test import override_settings

from ..models import BookDetail
from ..tasks import download_external_image

GOOGLE_TITLE = 'Чернильная кровь'
GOOGLE_AUTHOR = 'Корнелия Функе'
GOOGLE_BOOK_ID = 'C3hWAgAAQBAJ'
GOOGLE_IMAGE_URL = 'http://books.google.com/books/content?id=C3hWAgAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl'


class DownloadExternalImageText(TestCase):
    def setUp(self):
        detail = BookDetail.objects.create(
            title=GOOGLE_TITLE,
            author=GOOGLE_AUTHOR,
            external_id=GOOGLE_BOOK_ID,
            image_external_url=GOOGLE_IMAGE_URL
        )

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_download_correct(self):
        detail = BookDetail.objects.get(external_id=GOOGLE_BOOK_ID)
        download_external_image.apply(args=(detail.id, )).get()

        detail = BookDetail.objects.get(external_id=GOOGLE_BOOK_ID)
        self.assertIn('book_' + str(detail.id), detail.image.name)

