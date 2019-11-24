import requests
import logging

from django.http.response import JsonResponse
from django.views import View

from apps.utils.auth import auth_decorator
from PIL import Image

from ..serializers import BookSerializer
from ..forms import AddBookForm
from ..tasks import download_external_image

from ..models import Book, BookAudit


GOOGLE_VOLUME_API = "https://www.googleapis.com/books/v1/volumes/{}"


class AddMyBookView(View):
    @auth_decorator
    def post(self, request, *args, **kwargs):
        form = AddBookForm(request.POST, request.FILES)

        if not form.is_valid():
            return JsonResponse({'success': False, 'error_type': 'FORM_NOT_VALID', 'errors': form.errors})
        if self._already_added(form):
            return JsonResponse({'success': False, 'error_type': 'ALREADY_ADDED',
                                 'title': form.cleaned_data['title'], 'author': form.cleaned_data['author']})

        book = Book(
            account_id=self.request.session['account_id'],
            title=form.cleaned_data['title'],
            author=form.cleaned_data['author'],
            description=form.cleaned_data['description'],
            comment=form.cleaned_data['comment']
        )

        if form.cleaned_data['external_id']:
            book.source = Book.SOURCE.GOOGLE
            book.external_id = form.cleaned_data['external_id']
        else:
            book.source = Book.SOURCE.CUSTOM

        book.save()

        if form.cleaned_data['image']:
            self._save_custom_image(book, form)
        elif form.cleaned_data['external_image']:
            self._save_external_image(book, form)

        BookAudit.create_audit(book, self.request.session.get('vk_session_id'),
                                   BookAudit.ACTION_TYPE.ADD)
        return JsonResponse({'success': True, 'book': BookSerializer.serialize(book)})

    def _already_added(self, form):
        return Book.objects.filter(
            account_id=self.request.session['account_id'],
            status__in=[Book.STATUS.ACTIVE, Book.STATUS.NOT_ACTIVE],
            title=form.cleaned_data['title'],
            author=form.cleaned_data['author']
        ).exists()

    def _save_custom_image(self, book, form):
        from io import BytesIO
        from django.core.files import File
        if form.cleaned_data['image']:
            image = Image.open(form.cleaned_data['image'])
            size = 170, 250
            image.thumbnail(size)
            blob = BytesIO()
            image.save(blob, 'JPEG')
            book.image.save('book_{}.jpg'.format(book.id), File(blob), save=True)

    def _save_external_image(self, book, form):
        book.image_external_url = form.cleaned_data['external_image']
        book.save()
        download_external_image.delay(book.pk)
