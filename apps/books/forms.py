from django import forms


class AddBookForm(forms.Form):
    title = forms.CharField(max_length=255)
    author = forms.CharField(max_length=255, required=False)
    comment = forms.CharField(max_length=1024, required=False)
    external_id = forms.CharField(max_length=255, required=False)
