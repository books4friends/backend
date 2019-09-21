from django import forms

from apps.accounts.models import Account


class PrivacySomeFriends(forms.Form):
    selected_friends = forms.Field()


class LocaleForm(forms.Form):
    locale = forms.ChoiceField(choices=Account.LOCALE_CHOICES)
