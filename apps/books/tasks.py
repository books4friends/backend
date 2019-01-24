
from __future__ import absolute_import, unicode_literals
from celery import shared_task

import urllib.request
import imghdr

from django.core.files import File

from .models import BookDetail


@shared_task
def download_exteranl_image(book_detail_id):
    book = BookDetail.objects.get(pk=book_detail_id)
    image = urllib.request.urlretrieve(book.image_external_url)
    file = File(open(image[0], 'rb'))
    file_name = "{}_small.{}".format(book.external_id, imghdr.what(file))
    book.image.save(file_name, file)
    book.save()
