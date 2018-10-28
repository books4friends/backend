from django.db import models


class Account(models.Model):
    class VISIBILITY_TYPE:
        ALL_FRIENDS = 0
        ONLY_OWNER = 1
        ONLY_SOME_FRIENDS = 2
        ONLY_SOME_FRIENDS_LISTS = 3
    VISIBILITY_TYPE_CHOICES = (
        (VISIBILITY_TYPE.ALL_FRIENDS, 'all friends'),
        (VISIBILITY_TYPE.ONLY_OWNER, 'all friends'),
        (VISIBILITY_TYPE.ONLY_SOME_FRIENDS, 'only some friends'),
        (VISIBILITY_TYPE.ONLY_SOME_FRIENDS_LISTS, 'only some friends lists'),
    )

    vk_id = models.CharField(max_length=255)
    visibility_type = models.SmallIntegerField(choices=VISIBILITY_TYPE_CHOICES, default=VISIBILITY_TYPE.ALL_FRIENDS)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class WhiteListOfFriendsLists(models.Model):
    owner_id = models.ForeignKey(Account, on_delete=models.CASCADE)
    friend_id = models.CharField(max_length=255)


class WhiteListOfLists(models.Model):
    owner_id = models.ForeignKey(Account, on_delete=models.CASCADE)
    friend_list_id = models.CharField(max_length=255)
