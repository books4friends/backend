from django import forms

import datetime
from .models import BorrowReview


class CreateBorrowFrom(forms.Form):
    book_id = forms.IntegerField(required=True)
    planned_return_date = forms.DateField(required=True)

    def clean(self):
        planned_return_date = self.cleaned_data.get("planned_return_date")
        current_date = datetime.datetime.now().date()
        if planned_return_date < current_date :
            msg = u"planned_return_date should be greater than current date."
            self._errors["planned_return_date "] = self.error_class([msg])


class CreateBorrowReviewForm(forms.Form):
    keeping = forms.ChoiceField(choices=BorrowReview.KEEPING_CHOICES)
    time = forms.ChoiceField(choices=BorrowReview.TIME_CHOICES)
