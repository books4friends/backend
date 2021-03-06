from django.test import TestCase

import os
import tempfile
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import override_settings

from apps.frontend.tests.utils import AuthMixin
from apps.accounts.models import Account
from apps.books.models import Book

VK_ID = 'VK_ID'
TITLE = 'Ходячий замок'
AUTHOR = 'Диана Уинн Джонс'
GENRE = 9
DESCRIPTION = 'Книги английской писательницы Дианы У. Джонс настолько ярки, что так и просятся на экран. По ее бестселлеру "Ходячий замок" знаменитый мультипликатор Хаяо Миядзаки ("Унесенные призраками"), обладатель "Золотого льва" - высшей награды Венецианского фестиваля, снял анимационный фильм, побивший в Японии рекорды кассовых сборов. Софи живет в сказочной стране, где ведьмы и русалки, семимильные сапоги и говорящие собаки - обычное дело. Поэтому, когда на нее обрушивается ужасное проклятие коварной Болотной Ведьмы, Софи ничего не остается, как обратиться за помощью к таинственному чародею Хоулу, обитающему в ходячем замке. Однако, чтобы освободиться от чар, Софи предстоит разгадать немало загадок и прожить в замке у Хоула гораздо дольше, чем она рассчитывала. А для этого нужно подружиться с огненным демоном, поймать падучую звезду, подслушать пение русалок, отыскать мандрагору и многое, многое другое.'
COMMENT = 'Могу подарить'
IMAGE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/custom_image.jpg')
GOOGLE_TITLE = 'Чернильная кровь'
GOOGLE_AUTHOR = 'Корнелия Функе'
GOOGLE_BOOK_ID = 'C3hWAgAAQBAJ'
GOOGLE_DESCRIPTION = '«Чернильная кровь» — вторая часть трилогии знаменитой немецкой писательницы Корнелии Функе. Все поклонники ее творчества с удовольствием прочтут продолжение детективной истории героев «Чернильного сердца», ставшего событием не только в истории жанра фэнтези, но и вообще в книжном мире. Во второй части рассказывается о приключениях героев, попавших в Чернильный мир - мир из бумаги и типографской краски. Сажерук возвращается домой. Фарид и Мегги следуют за ним, а вскоре туда отправляются и родители Мегги. В этом мире, сочиненном Фенолио, где живут феи и русалки, так легко погибнуть по произволу злого правителя. Героев ждут нелегкие испытания, но они достойно встречают их, обнаруживая в себе качества, о которых и не подозревали.'
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
        response = self.client.post('/api/app/my-books/add/', {
            'title': TITLE,
            'author': AUTHOR,
            'comment': COMMENT,
            'genre': GENRE,
            'description': DESCRIPTION,
            'image': custom_image,
        })
        self.assertEqual(account.books.all().count(), 1)
        book = account.books.all()[0]

        self.assertEqual(book.title, TITLE)
        self.assertEqual(book.author, AUTHOR)
        self.assertEqual(book.genre, GENRE)
        self.assertEqual(book.description, DESCRIPTION)
        self.assertEqual(book.source, Book.SOURCE.CUSTOM)
        self.assertIn('book_' + str(book.id), book.image.name)
        self.assertEqual(book.comment, COMMENT)
        self.assertEqual(book.status, Book.STATUS.ACTIVE)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "success": True,
                "book": {
                    "id": str(book.id),
                    "description": {
                        "title": TITLE, "author": AUTHOR, "description": DESCRIPTION,
                        "genre": GENRE, "image": book.image.url,
                    },
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
        response = self.client.post('/api/app/my-books/add/', {
            'title': TITLE,
            'author': AUTHOR,
            'description': DESCRIPTION,
            'genre': GENRE,
            'image': custom_image,
        })
        self.assertEqual(account.books.all().count(), 1)
        book = account.books.all()[0]

        self.assertEqual(book.title, TITLE)
        self.assertEqual(book.author, AUTHOR)
        self.assertEqual(book.description, DESCRIPTION)
        self.assertEqual(book.genre, GENRE)
        self.assertEqual(book.source, Book.SOURCE.CUSTOM)
        self.assertIn('book_' + str(book.id), book.image.name)
        self.assertEqual(book.comment, '')
        self.assertEqual(book.status, Book.STATUS.ACTIVE)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "success": True,
                "book": {
                    "id": str(book.id),
                    "description": {
                        "title": TITLE, "author": AUTHOR, "description": DESCRIPTION,
                        "image": book.image.url, "genre": GENRE,
                    },
                    "comment": "",
                    "active": True
                }
            }
        )

    @override_settings(MEDIA_ROOT=tempfile.gettempdir())
    def test_adding_with_full_correct_data_and_custom_image_no_author_and_description(self):
        account = Account.objects.get(vk_id=VK_ID)
        self.auth_user(account)

        custom_image = SimpleUploadedFile(
            name='test_image.jpg', content=open(IMAGE_PATH, 'rb').read(), content_type='image/jpeg')
        response = self.client.post('/api/app/my-books/add/', {
            'title': TITLE,
            'comment': COMMENT,
            'genre': GENRE,
            'image': custom_image
        })
        self.assertEqual(account.books.all().count(), 1)
        book = account.books.all()[0]

        self.assertEqual(book.title, TITLE)
        self.assertEqual(book.author, '')
        self.assertEqual(book.genre, GENRE)
        self.assertEqual(book.source, Book.SOURCE.CUSTOM)
        self.assertIn('book_' + str(book.id), book.image.name)
        self.assertEqual(book.comment, COMMENT)
        self.assertEqual(book.status, Book.STATUS.ACTIVE)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "success": True,
                "book": {
                    "id": str(book.id),
                    "description": {"title": TITLE, "author": "", "description": "",
                                    "image": book.image.url, "genre": GENRE, },
                    "comment": COMMENT,
                    "active": True
                }
            }
        )

    def test_no_data(self):
        account = Account.objects.get(vk_id=VK_ID)
        self.auth_user(account)
        response = self.client.post('/api/app/my-books/add/', {})

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "success": False,
                "error_type": "FORM_NOT_VALID",
                "errors": {"title": ["Обязательное поле."]}
            }
        )

    @override_settings(LANGUAGE_CODE='en-US', LANGUAGES=(('en', 'English'),))
    def test_no_data_english(self):
        account = Account.objects.get(vk_id=VK_ID)
        self.auth_user(account)
        response = self.client.post('/api/app/my-books/add/', {})

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

        response = self.client.post('/api/app/my-books/add/', {
            'title': GOOGLE_TITLE,
            'author': GOOGLE_AUTHOR,
            'description': GOOGLE_DESCRIPTION,
            'external_id': GOOGLE_BOOK_ID,
            'external_image': GOOGLE_IMAGE_URL,
            'comment': COMMENT,
        })
        self.assertEqual(account.books.all().count(), 1)
        book = account.books.all()[0]

        self.assertEqual(book.title, GOOGLE_TITLE)
        self.assertEqual(book.author, GOOGLE_AUTHOR)
        self.assertEqual(book.description, GOOGLE_DESCRIPTION)
        self.assertEqual(book.source, Book.SOURCE.GOOGLE)
        self.assertIn(GOOGLE_IMAGE_URL, book.image_external_url)
        self.assertEqual(book.comment, COMMENT)
        self.assertEqual(book.status, Book.STATUS.ACTIVE)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "success": True,
                "book": {
                    "id": str(book.id),
                    "description": {
                        "title": GOOGLE_TITLE,
                        "author": GOOGLE_AUTHOR,
                        "description": GOOGLE_DESCRIPTION,
                        "image": book.image_external_url,
                        "genre": None,
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

        response = self.client.post('/api/app/my-books/add/', {
            'title': GOOGLE_TITLE,
            'author': GOOGLE_AUTHOR,
            'external_image': GOOGLE_IMAGE_URL,
            'comment': COMMENT,
        })
        self.assertEqual(account.books.all().count(), 1)
        book = account.books.all()[0]

        self.assertEqual(book.title, GOOGLE_TITLE)
        self.assertEqual(book.author, GOOGLE_AUTHOR)
        self.assertEqual(book.source, Book.SOURCE.CUSTOM)
        self.assertIn(GOOGLE_IMAGE_URL, book.image_external_url)
        self.assertEqual(book.comment, COMMENT)
        self.assertEqual(book.status, Book.STATUS.ACTIVE)

        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "success": True,
                "book": {
                    "id": str(book.id),
                    "description": {
                        "title": GOOGLE_TITLE,
                        "author": GOOGLE_AUTHOR,
                        "description": "",
                        "image": book.image_external_url,
                        "genre":  None,
                    },
                    "comment": COMMENT,
                    "active": True
                }
            }
        )
