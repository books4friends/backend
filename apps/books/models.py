from django.db import models

import json

from django.core.serializers.json import DjangoJSONEncoder

from apps.accounts.models import VkSession


class Book(models.Model):
    class STATUS:
        ACTIVE = 0
        NOT_ACTIVE = 1
        DELETED = 2
    STATUS_CHOICES = (
        (STATUS.ACTIVE, "active"),
        (STATUS.NOT_ACTIVE, "not active"),
        (STATUS.DELETED, "deleted"),
    )

    class SOURCE:
        CUSTOM = 0
        GOOGLE = 1
    SOURCE_CHOICES = (
        (SOURCE.CUSTOM, 'custom'),
        (SOURCE.GOOGLE, 'google'),
    )

    GENRES = ['action', 'adventures', 'biographies', 'business', 'children', 'classics', 'comics', 'culture',
              'detectives', 'fantasy', 'hobby', 'language', 'modern_prose', 'poetry', 'popular_science', 'psychology',
              'romance', 'education']

    GENRE_CHOICES = tuple((index, key) for index, key in enumerate(GENRES))

    account = models.ForeignKey('accounts.Account', on_delete=models.PROTECT, related_name='books')

    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, null=True, blank=True)
    description = models.TextField()
    genre = models.SmallIntegerField(choices=GENRE_CHOICES, null=True)  # None is Other genre
    source = models.SmallIntegerField(choices=SOURCE_CHOICES, default=SOURCE.CUSTOM)
    external_id = models.CharField(max_length=255, unique=True, null=True)
    image = models.ImageField(upload_to='books/', null=True)
    image_external_url = models.URLField(max_length=512, null=True, blank=True)

    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS.ACTIVE)
    comment = models.TextField()

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ('-created_at', )


class BookAudit(models.Model):
    class ACTION_TYPE(object):
        ADD = 0
        ACTIVATE = 1
        DEACTIVATE = 2
        UPDATE_COMMENT = 3
        DELETE = 4

    ACTION_TYPE_CHOICES = (
        (ACTION_TYPE.ADD, 'add'),
        (ACTION_TYPE.ACTIVATE, 'activate'),
        (ACTION_TYPE.DEACTIVATE, 'deactivate'),
        (ACTION_TYPE.UPDATE_COMMENT, 'update_comment'),
        (ACTION_TYPE.DELETE, 'delete'),
    )

    book = models.ForeignKey('Book', on_delete=models.CASCADE)
    vk_session = models.ForeignKey(VkSession, on_delete=models.PROTECT)
    action_type = models.SmallIntegerField(choices=ACTION_TYPE_CHOICES)
    dump = models.TextField("Dump")
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create_audit(cls, book, vk_session_id, action_type):
        log = BookAudit()
        log.book = book
        log.vk_session_id = vk_session_id
        log.action_type = action_type
        log.dump = json.dumps(
            list(Book.objects.filter(id=book.id).values()),
            cls=DjangoJSONEncoder
        )
        log.save()
