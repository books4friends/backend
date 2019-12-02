from django.db import models

from apps.books.models import Book
from apps.accounts.models import Account


class Borrow(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrower = models.ForeignKey(Account, on_delete=models.CASCADE)
    take_date = models.DateField(auto_now_add=True)
    planned_return_date = models.DateField()
    real_return_date = models.DateField(null=True)
