import json
import requests
import urllib.request
import imghdr
import logging

from django.http.response import JsonResponse
from django.views import View
from django.core.files import File

from apps.utils.auth import auth_decorator

from ..serializers import BookItemSerializer
from ..forms import AddBookForm

from ..models import BookDetail, BookItem


GOOGLE_VOLUME_API = "https://www.googleapis.com/books/v1/volumes/{}"


class AddBookView(View):
    @auth_decorator
    def post(self, request, *args, **kwargs):
        data = json.loads(request.body.decode('utf-8'))
        form = AddBookForm(data)
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
            image = urllib.request.urlretrieve(google_data['image_url'],)
            file = File(open(image[0], 'rb'))
            file_name = "{}_small.{}".format(google_id, imghdr.what(file))
            book_detail.image.save(file_name, file)
            book_detail.save()
        return book_detail

    def _get_or_create_custom_book(self, form):
        book_detail, _ = BookDetail.objects.get_or_create(
            source=BookDetail.SOURCE.CUSTOM,
            title=form.cleaned_data['title'],
            author=form.cleaned_data['author'],
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
