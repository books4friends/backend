from django.db import models

from apps.books.models import Book
from apps.accounts.models import Account


class Borrow(models.Model):
    class STATUS:
        NEW = 0
        Approve = 1
        RETURNED = 10
        CANCELED = 21
        REJECTED = 22

    STATUS_CHOICES = (
        (STATUS.NEW, "new"),
        (STATUS.Approve, "approved"),
        (STATUS.RETURNED, "returned"),
        (STATUS.CANCELED, "canceled"),
        (STATUS.REJECTED, "rejected"),
    )
    VISIBLE_STATUSES = [STATUS.NEW, STATUS.Approve, STATUS.RETURNED]

    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrower = models.ForeignKey(Account, on_delete=models.CASCADE)
    take_date = models.DateField(auto_now_add=True)
    planned_return_date = models.DateField()
    real_return_date = models.DateField(null=True)
    status = models.PositiveSmallIntegerField(default=STATUS.NEW, choices=STATUS_CHOICES)

    class Meta:
        ordering = ('-id',)
