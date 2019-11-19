import requests
import logging

from django.http.response import JsonResponse
from django.views import View

from apps.utils.auth import auth_decorator
from PIL import Image

from ..serializers import BookItemSerializer
from ..forms import AddBookForm
from ..tasks import download_external_image

from ..models import BookDetail, BookItem, BookItemAudit


GOOGLE_VOLUME_API = "https://www.googleapis.com/books/v1/volumes/{}"


class AddMyBookView(View):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.external_image = None

    @auth_decorator
    def post(self, request, *args, **kwargs):
        form = AddBookForm(request.POST, request.FILES)
        if form.is_valid():
            if BookItem.objects.filter(
                account_id=self.request.session['account_id'],
                status__in=[BookItem.STATUS.ACTIVE, BookItem.STATUS.NOT_ACTIVE],
                detail__title=form.cleaned_data['title'],
                detail__author=form.cleaned_data['author']
            ).exists():
                return JsonResponse({'success': False, 'error_type': 'ALREADY_ADDED',
                                     'title': form.cleaned_data['title'], 'author': form.cleaned_data['author']})

            if form.cleaned_data['external_id']:
                try:
                    book_detail = self._get_or_create_google_book(form.cleaned_data['external_id'])
                except Exception as e:
                    logging.error(e, exc_info=True)
                    book_detail = self._get_or_create_custom_book(form)
            else:
                book_detail = self._get_or_create_custom_book(form)

            book_item = BookItem.objects.create(
                detail=book_detail,
                account_id=self.request.session['account_id'],
                comment=form.cleaned_data['comment']
            )
            self._save_image(book_item, form)
            self._save_external_image(book_item, form)
            BookItemAudit.create_audit(book_item, self.request.session.get('vk_session_id'),
                                       BookItemAudit.ACTION_TYPE.ADD)
            return JsonResponse({'success': True, 'book': BookItemSerializer.serialize(book_item)})
        else:
            return JsonResponse({'success': False, 'error_type': 'FORM_NOT_VALID', 'errors': form.errors})

    def _get_or_create_google_book(self, google_id):
        try:
            book_detail = BookDetail.objects.get(
                source=BookDetail.SOURCE.GOOGLE,
                external_id=google_id,
            )
        except BookDetail.DoesNotExist:
            google_data = self._get_google_book(google_id)
            book_detail = BookDetail(
                source=BookDetail.SOURCE.GOOGLE,
                external_id=google_id,
                title=google_data['title'],
                author=google_data['author'],
            )
            self.external_image = google_data['image_url']
            book_detail.save()
            download_external_image.delay(book_detail.id)
        return book_detail

    def _get_or_create_custom_book(self, form):
        if form.cleaned_data['image']:
            book_detail = BookDetail.objects.create(
                source=BookDetail.SOURCE.CUSTOM,
                title=form.cleaned_data['title'],
                author=form.cleaned_data['author']
            )
        else:
            book_detail, _ = BookDetail.objects.get_or_create(
                source=BookDetail.SOURCE.CUSTOM,
                title=form.cleaned_data['title'],
                author=form.cleaned_data['author'],
            )
        return book_detail

    def _save_image(self, book_item, form):
        from io import BytesIO
        from django.core.files import File
        if form.cleaned_data['image']:
            image = Image.open(form.cleaned_data['image'])
            size = 170, 250
            image.thumbnail(size)
            blob = BytesIO()
            image.save(blob, 'JPEG')
            book_item.image.save('book_{}.jpg'.format(book_item.id), File(blob), save=True)

    def _save_external_image(self, book_item, form):
        if self.external_image:
            book_item.image_external_url = self.external_image
            book_item.save()

    def _get_google_book(self, google_id):
        response = requests.get(GOOGLE_VOLUME_API.format(google_id))
        if response.status_code == 200:
            data = response.json()['volumeInfo']
            return {
                'title': data['title'],
                'author': ", ".join(data['authors']) if 'authors' in data else None,
                'image_url': data['imageLinks']['thumbnail']
            }
        else:
            raise self.GoogleException

    class GoogleException(Exception):
        pass
