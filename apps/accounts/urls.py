from django.conf.urls import url

from .views.friends_list_view import FriendsListView
from .views.account_settings_view import AccountSettingsView


urlpatterns = [
    url(r'^friends-list/$', FriendsListView.as_view(), name='friends-list'),
    url(r'^$', AccountSettingsView.as_view(), name='account-settings'),
]
