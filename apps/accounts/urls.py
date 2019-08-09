from django.conf.urls import url

from .views.friends_list_view import FriendsListView
from .views.account_settings_view import AccountSettingsView
from .views.update_privacy_settings_view import SetPrivacyAllFriendsView, SetPrivacySomeFriendsView


urlpatterns = [
    url(r'^friends-list/$', FriendsListView.as_view(), name='friends-list'),
    url(r'^privacy/set-all-friends/$', SetPrivacyAllFriendsView.as_view(), name='set-privacy-all-friends/'),
    url(r'^privacy/set-some-friends/$', SetPrivacySomeFriendsView.as_view(), name='set-privacy-some-friends/'),
    url(r'^$', AccountSettingsView.as_view(), name='account-settings'),
]
