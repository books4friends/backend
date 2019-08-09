from django.conf.urls import url

from .views.friends_list_view import FriendsListView


urlpatterns = [
    url(r'^friends-list/$', FriendsListView.as_view(), name='friends-list'),
]
