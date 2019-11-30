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
DESCRIPTION = 'Книги английской писательницы Дианы У. Джонс настолько ярки, что так и просятся на экран. По ее бестселлеру "Ходячий замок" знаменитый мультипликатор Хаяо Миядзаки ("Унесенные призраками"), обладатель "Золотого льва" - высшей награды Венецианского фестиваля, снял анимационный фильм, побивший в Японии рекорды кассовых сборов. Софи живет в сказочной стране, где ведьмы и русалки, семимильные сапоги и говорящие собаки - обычное дело. Поэтому, когда на нее обрушивается ужасное проклятие коварной Болотной Ведьмы, Софи ничего не остается, как обратиться за помощью к таинственному чародею Хоулу, обитающему в ходячем замке. Однако, чтобы освободиться от чар, Софи предстоит разгадать немало загадок и прожить в замке у Хоула гораздо дольше, чем она рассчитывала. А для этого нужно подружиться с огненным демоном, поймать падучую звезду, подслушать пение русалок, отыскать мандрагору и многое, многое другое.'
GENRE = 9
TITLE_2 = 'Мать'
AUTHOR_2 = 'Максим Горький'
DESCRIPTION_2 = 'В романе изображена борьба революционеров-подпольщиков против царского правительства. Главная героиня – мать лидера революционного движения рабочих предместий, пожилая жительница, проникшаяся идеями своего сына и его товарищей о справедливости, правде, борьбе за лучшую жизнь. Сначала страшась, но постепенно вливаясь в волну народного неприятия и нарастающего сопротивления сложившейся мрачной и убогой жизни, уготованной ему власть имущими и хозяевами жизни, вставшая в ряды революционеров вслед за своим сыном, невзирая на неотвратимо грядущие поимку жандармами, несправедливый суд.'
GENRE_2 = 5
TITLE_3 = 'Манюня'
AUTHOR_3 = 'Наринэ Абгарян'
DESCRIPTION_3 = '"Манюня" - светлый, пропитанный солнцем и запахами южного базара и потрясающе смешной рассказ о детстве, о двух девочках-подружках Наре и Манюне, о грозной и доброй Ба - бабушке Манюни, и о куче их родственников, постоянно попадающих в казусные ситуации. Это то самое теплое, озорное и полное веселых приключений детство, которое делает человека счастливым на всю жизнь.'
GENRE_3 = 12
COMMENT = 'Могу подарить'
IMAGE_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'tests/custom_image.jpg')
GOOGLE_IMAGE_URL = 'http://books.google.com/books/content?id=C3hWAgAAQBAJ&printsec=frontcover&img=1&zoom=1&edge=curl'


class MyBooksListViewTest(TestCase, AuthMixin):
    def setUp(self):
        self.account = Account.objects.create(vk_id=VK_ID)

    def test_url_exists_at_desired_location(self):
        self.auth_user(self.account)
        response = self.client.get('/api/app/my-books/')
        self.assertEqual(response.status_code, 200)

    def test_custom_book(self):
        custom_image = SimpleUploadedFile(
            name='test_image.jpg', content=open(IMAGE_PATH, 'rb').read(), content_type='image/jpeg')
        book = Book.objects.create(
            account=self.account,
            title=TITLE,
            author=AUTHOR,
            description=DESCRIPTION,
            genre=GENRE,
            image=custom_image,
        )

        self.auth_user(self.account)
        response = self.client.get('/api/app/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": [{
                    "id": str(book.id),
                    "description": {
                        "title": TITLE, "author": AUTHOR, "image": book.image.url, "description": DESCRIPTION,
                        "genre": GENRE,
                    },
                    "comment": '',
                    "active": True
                }]
            }
        )

    def test_book_with_downloaded_image_and_external_image(self):
        custom_image = SimpleUploadedFile(
            name='test_image.jpg', content=open(IMAGE_PATH, 'rb').read(), content_type='image/jpeg'
        )
        book = self.book = Book.objects.create(
            account=self.account,
            image=custom_image,
            image_external_url=GOOGLE_IMAGE_URL,
            title=TITLE,
            author=AUTHOR,
            genre=GENRE,
            description=DESCRIPTION,
            source=Book.SOURCE.GOOGLE,
        )

        self.auth_user(self.account)
        response = self.client.get('/api/app/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": [{
                    "id": str(book.id),
                    "description": {
                        "title": TITLE,
                        "author": AUTHOR,
                        "description": DESCRIPTION,
                        "image": book.image.url,
                        "genre": GENRE,
                    },
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
            description=DESCRIPTION,
            genre=GENRE,
            source=Book.SOURCE.GOOGLE,
            image_external_url=GOOGLE_IMAGE_URL,
        )

        self.auth_user(self.account)
        response = self.client.get('/api/app/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": [{
                    "id": str(book.id),
                    "description": {
                        "title": TITLE, "author": AUTHOR, "image": GOOGLE_IMAGE_URL, "description": DESCRIPTION,
                        "genre": GENRE,
                    },
                    "comment": '',
                    "active": True
                }]
            }
        )

    def test_book_with_author_and_title(self):
        book = self.book = Book.objects.create(
            account=self.account,
            title=TITLE,
            author=AUTHOR,
        )

        self.auth_user(self.account)
        response = self.client.get('/api/app/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": [{
                    "id": str(book.id),
                    "description": {"title": TITLE, "author": AUTHOR, "description": "", "image": None, "genre": None},
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
        response = self.client.get('/api/app/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": [{
                    "id": str(book.id),
                    "description": {"title": TITLE, "author": AUTHOR, "description": "", "image": None, "genre": None},
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
        response = self.client.get('/api/app/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": [{
                    "id": str(book.id),
                    "description": {"title": TITLE, "author": AUTHOR, "description": "", "image": None, "genre": None},
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
        response = self.client.get('/api/app/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": [{
                    "id": str(book.id),
                    "description": {"title": TITLE, "author": None, "description": "", "image": None, "genre": None,},
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
        response = self.client.get('/api/app/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": [{
                    "id": str(book.id),
                    "description": {"title": TITLE, "author": AUTHOR, "description": "", "image": None, "genre": None},
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
        response = self.client.get('/api/app/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": []
            }
        )

    def test_no_books(self):
        self.auth_user(self.account)
        response = self.client.get('/api/app/my-books/')
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
        response = self.client.get('/api/app/my-books/')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(
            response.content.decode("utf-8"),
            {
                "books": []
            }
        )

    def test_a_few_book_list(self):
        book1 = self.book = Book.objects.create(
            account=self.account,
            title=TITLE,
            author=AUTHOR,
            description=DESCRIPTION,
            genre=GENRE,
        )
        book2 = self.book = Book.objects.create(
            account=self.account,
            title=TITLE_2,
            author=AUTHOR_2,
            description=DESCRIPTION_2,
            genre=GENRE_2,
            status=Book.STATUS.NOT_ACTIVE
        )
        book3 = self.book = Book.objects.create(
            account=self.account,
            title=TITLE_3,
            author=AUTHOR_3,
            description=DESCRIPTION_3,
            genre=GENRE_3,
            status=Book.STATUS.DELETED
        )

        self.auth_user(self.account)
        response = self.client.get('/api/app/my-books/')
        self.assertEqual(response.status_code, 200)

        import json

        response_json = json.loads(response.content)['books'],
        response_json = response_json[0]
        self.assertEquals(len(response_json), 2)
        self.assertEquals(
            response_json[1], {
                "id": str(book1.id),
                "description": {"title": TITLE, "author": AUTHOR, "description": DESCRIPTION, "genre": GENRE,
                                "image": None,},
                "comment": "",
                "active": True
            }
        )
        self.assertEquals(
            response_json[0], {
                "id": str(book2.id),
                "description": {"title": TITLE_2, "author": AUTHOR_2, "description": DESCRIPTION_2, "genre": GENRE_2,
                                "image": None,},
                "comment": "",
                "active": False
            }
        )
