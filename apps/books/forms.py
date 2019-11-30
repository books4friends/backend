from django import forms

from .models import Book


class AddBookForm(forms.Form):
    title = forms.CharField(max_length=255)
    author = forms.CharField(max_length=255, required=False)
    comment = forms.CharField(max_length=1024, required=False)
    description = forms.CharField(max_length=4096, required=False)
    genre = forms.ChoiceField(choices=Book.GENRE_CHOICES, required=False,)
    external_id = forms.CharField(max_length=255, required=False)
    image = forms.ImageField(required=False)
    external_image = forms.URLField(required=False)


class EditBookCommentForm(forms.Form):
    comment = forms.CharField(max_length=1024, required=True)
