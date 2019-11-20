from __future__ import absolute_import, unicode_literals
from celery import shared_task

import urllib.request
import imghdr

from django.core.files import File

from .models import BookDetail, BookItem


@shared_task
def download_external_image(book_id):
    book = BookItem.objects.get(pk=book_id)
    save_cover_book = BookItem.objects.filter(image_external_url=book.image_external_url).exclude(pk=book_id)
    if len(save_cover_book) > 0:
        book.image = save_cover_book[0].image.name
        book.save()
    else:
        image = urllib.request.urlretrieve(book.image_external_url)
        file = File(open(image[0], 'rb'))
        file_name = "book_g_{}.{}".format(book_id, imghdr.what(file))
        book.image.save(file_name, file)
        book.save()
