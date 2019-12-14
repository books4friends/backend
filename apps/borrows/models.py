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


class BorrowReview(models.Model):
    class KEEPING:
        SAME = 0
        SPOILED_A_LITTLE = 1
        SPOILED = 2
    KEEPING_CHOICES = (
        (KEEPING.SAME, 'same'),
        (KEEPING.SPOILED_A_LITTLE, 'spoiled a little'),
        (KEEPING.SPOILED, 'spoiled'),
    )

    class TIME:
        IN_TIME = 0
        LATE_A_LITTLE = 1
        LATE = 2
    TIME_CHOICES = (
        (TIME.IN_TIME, 'in time'),
        (TIME.LATE_A_LITTLE, 'late a little'),
        (TIME.LATE, 'late'),
    )

    borrow = models.ForeignKey(Borrow, on_delete=models.CASCADE)
    keeping = models.PositiveSmallIntegerField(default=KEEPING.SAME, choices=KEEPING_CHOICES)
    time = models.PositiveSmallIntegerField(default=TIME.IN_TIME, choices=TIME_CHOICES)

