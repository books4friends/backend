from django.conf.urls import url

from .views.account_settings_view import AccountSettingsView
from .views.update_locale_view import SetLocaleView
from .views.update_privacy_settings_view import PrivacyFriendsListView, SetPrivacyAllFriendsView, \
    SetPrivacySomeFriendsView, SetPrivacyExceptSomeFriendsView, SetPrivacyOnlyOwnerView


urlpatterns = [
    url(r'^$', AccountSettingsView.as_view(), name='account-settings'),
    url(r'^locale/set/$', SetLocaleView.as_view(), name='set-locale'),
    url(r'^privacy/friends/$', PrivacyFriendsListView.as_view(), name='privacy-friends-list'),
    url(r'^privacy/set-all-friends/$', SetPrivacyAllFriendsView.as_view(), name='set-privacy-all-friends/'),
    url(r'^privacy/set-some-friends/$', SetPrivacySomeFriendsView.as_view(), name='set-privacy-some-friends/'),
    url(r'^privacy/set-except-some-friends/$', SetPrivacyExceptSomeFriendsView.as_view(),
        name='set-except-privacy-some-friends/'),
    url(r'^privacy/set-only-owner/$', SetPrivacyOnlyOwnerView.as_view(), name='set-privacy-only-owner/'),
]
