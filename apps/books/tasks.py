from __future__ import absolute_import, unicode_literals
from celery import shared_task

import urllib.request
import imghdr

from django.core.files import File

from .models import BookDetail, BookItem


@shared_task
def download_external_image(book_id):
    book = BookItem.objects.get(pk=book_id)
    image = urllib.request.urlretrieve(book.image_external_url)
    file = File(open(image[0], 'rb'))
    file_name = "book_g_{}.{}".format(book_id, imghdr.what(file))
    book.image.save(file_name, file)
    book.save()
