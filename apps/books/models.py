from django.db import models


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
        ADDED = 0
        UPDATED = 1

    ACTION_TYPE_CHOICES = (
        (ACTION_TYPE.ADDED, 'added'),
        (ACTION_TYPE.UPDATED, 'updated'),
    )

    book_detail = models.ForeignKey('BookDetail', on_delete=models.CASCADE)
    action_type = models.SmallIntegerField(choices=ACTION_TYPE_CHOICES)
    description = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
