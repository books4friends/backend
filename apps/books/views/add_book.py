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
    @auth_decorator
    def post(self, request, *args, **kwargs):
        form = AddBookForm(request.POST, request.FILES)
        if form.is_valid():
            if self._already_added(form):
                return JsonResponse({'success': False, 'error_type': 'ALREADY_ADDED',
                                     'title': form.cleaned_data['title'], 'author': form.cleaned_data['author']})

            book_detail = self._get_or_create_book(form)

            book_item = BookItem.objects.create(
                detail=book_detail,
                account_id=self.request.session['account_id'],
                comment=form.cleaned_data['comment']
            )

            if form.cleaned_data['external_id']:
                book_detail.source = BookDetail.SOURCE.GOOGLE
                book_detail.external_id = form.cleaned_data['external_id']
                book_detail.save()

            if form.cleaned_data['image']:
                self._save_image(book_item, form)
            elif form.cleaned_data['external_image']:
                self._save_external_image(book_item, form)

            BookItemAudit.create_audit(book_item, self.request.session.get('vk_session_id'),
                                       BookItemAudit.ACTION_TYPE.ADD)
            return JsonResponse({'success': True, 'book': BookItemSerializer.serialize(book_item)})
        else:
            return JsonResponse({'success': False, 'error_type': 'FORM_NOT_VALID', 'errors': form.errors})

    def _already_added(self, form):
        return BookItem.objects.filter(
            account_id=self.request.session['account_id'],
            status__in=[BookItem.STATUS.ACTIVE, BookItem.STATUS.NOT_ACTIVE],
            detail__title=form.cleaned_data['title'],
            detail__author=form.cleaned_data['author']
        ).exists()

    def _get_or_create_book(self, form):
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
        book_item.image_external_url = form.cleaned_data['external_image']
        book_item.save()
        download_external_image(book_item.pk)
