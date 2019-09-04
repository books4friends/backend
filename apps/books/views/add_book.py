import json
import requests
import logging

from django.http.response import JsonResponse
from django.views import View

from apps.utils.auth import auth_decorator
from sorl.thumbnail import get_thumbnail
from PIL import Image

from ..serializers import BookItemSerializer
from ..forms import AddBookForm
from ..tasks import download_exteranl_image

from ..models import BookDetail, BookItem, BookItemAudit


GOOGLE_VOLUME_API = "https://www.googleapis.com/books/v1/volumes/{}"


class AddBookView(View):
    @auth_decorator
    def post(self, request, *args, **kwargs):
        form = AddBookForm(request.POST, request.FILES)
        if form.is_valid():
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
            BookItemAudit.create_audit(book_item, self.request.session.get('vk_session_id'),
                                       BookItemAudit.ACTION_TYPE.ADD)
            return JsonResponse({'success': True, 'book': BookItemSerializer.serialize(book_item)})
        else:
            return JsonResponse({'success': False, 'errors': form.errors})

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
                image_external_url=google_data['image_url'],
            )
            book_detail.save()
            download_exteranl_image.delay(book_detail.id)
        return book_detail

    def _get_or_create_custom_book(self, form):
        from io import BytesIO
        from django.core.files import File

        if form.cleaned_data['image']:
            image = Image.open(form.cleaned_data['image'])
            size = 170, 250
            image.thumbnail(size)
            blob = BytesIO()
            image.save(blob, 'JPEG')

            book_detail = BookDetail.objects.create(
                source=BookDetail.SOURCE.CUSTOM,
                title=form.cleaned_data['title'],
                author=form.cleaned_data['author']
            )
            book_detail.image.save('book_{}.jpg'.format(book_detail.id), File(blob), save=True)
        else:
            book_detail, _ = BookDetail.objects.get_or_create(
                source=BookDetail.SOURCE.CUSTOM,
                title=form.cleaned_data['title'],
                author=form.cleaned_data['author'],
                image=None
            )
        return book_detail

    def _get_google_book(self, google_id):
        response = requests.get(GOOGLE_VOLUME_API.format(google_id))
        if response.status_code == 200:
            data = response.json()['volumeInfo']
            return {
                'title': data['title'],
                'author': ", ".join(data['authors']) if 'authors' in data else None,
                'image_url': data['imageLinks']['small']
            }
        else:
            raise self.GoogleException

    class GoogleException(Exception):
        pass
