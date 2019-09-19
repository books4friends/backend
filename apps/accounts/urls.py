from django.conf.urls import url

from .views.account_settings_view import AccountSettingsView
from .views.update_privacy_settings_view import PrivacyFriendsListView, SetPrivacyAllFriendsView, \
    SetPrivacySomeFriendsView, SetPrivacyExceptSomeFriendsView, SetPrivacyOnlyOwnerView


urlpatterns = [
    url(r'^friends-list/$', PrivacyFriendsListView.as_view(), name='friends-list'),
    url(r'^privacy/set-all-friends/$', SetPrivacyAllFriendsView.as_view(), name='set-privacy-all-friends/'),
    url(r'^privacy/set-some-friends/$', SetPrivacySomeFriendsView.as_view(), name='set-privacy-some-friends/'),
    url(r'^privacy/set-except-some-friends/$', SetPrivacyExceptSomeFriendsView.as_view(),
        name='set-except-privacy-some-friends/'),
    url(r'^privacy/set-only-owner/$', SetPrivacyOnlyOwnerView.as_view(), name='set-privacy-only-owner/'),
    url(r'^$', AccountSettingsView.as_view(), name='account-settings'),
]
