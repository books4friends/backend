from django.db import models

import json

from django.core.serializers.json import DjangoJSONEncoder

from apps.accounts.models import VkSession


class BookDetail(models.Model):
    class SOURCE:
        CUSTOM = 0
        GOOGLE = 1
    SOURCE_CHOICES = (
        (SOURCE.CUSTOM, 'custom'),
        (SOURCE.GOOGLE, 'google'),
    )
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255, null=True, blank=True)
    image = models.ImageField(upload_to='books/', null=True)
    image_external_url = models.URLField(max_length=512, null=True, blank=True)
    source = models.SmallIntegerField(choices=SOURCE_CHOICES, default=SOURCE.CUSTOM)
    external_id = models.CharField(max_length=255, unique=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class BookItem(models.Model):
    class STATUS:
        ACTIVE = 0
        NOT_ACTIVE = 1
        DELETED = 2
    STATUS_CHOICES = (
        (STATUS.ACTIVE, "active"),
        (STATUS.NOT_ACTIVE, "not active"),
        (STATUS.DELETED, "deleted"),
    )

    detail = models.ForeignKey('BookDetail', on_delete=models.PROTECT)
    account = models.ForeignKey('accounts.Account', on_delete=models.PROTECT)
    status = models.SmallIntegerField(choices=STATUS_CHOICES, default=STATUS.ACTIVE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    comment = models.TextField()


class BookItemAudit(models.Model):
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

    book_item = models.ForeignKey('BookItem', on_delete=models.CASCADE)
    vk_session = models.ForeignKey(VkSession, on_delete=models.PROTECT)
    action_type = models.SmallIntegerField(choices=ACTION_TYPE_CHOICES)
    dump = models.TextField("Dump")
    created_at = models.DateTimeField(auto_now_add=True)

    @classmethod
    def create_audit(cls, book_item, vk_session_id, action_type):
        log = BookItemAudit()
        log.book_item = book_item
        log.vk_session_id = vk_session_id
        log.action_type = action_type
        log.dump = json.dumps(
            list(BookItem.objects.filter(id=book_item.id).values()),
            cls=DjangoJSONEncoder
        )
        log.save()
