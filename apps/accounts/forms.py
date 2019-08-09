from django import forms


class PrivacySomeFriends(forms.Form):
    selected_friends = forms.Field()
