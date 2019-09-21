from django.db import models


class Account(models.Model):
    class PRIVACY_TYPE:
        ALL_FRIENDS = 0
        ONLY_OWNER = 1
        ONLY_SOME_FRIENDS = 2
        EXCEPT_SOME_FRIENDS = 3
    PRIVACY_TYPE_CHOICES = (
        (PRIVACY_TYPE.ALL_FRIENDS, 'all friends'),
        (PRIVACY_TYPE.ONLY_OWNER, 'only me'),
        (PRIVACY_TYPE.ONLY_SOME_FRIENDS, 'only some friends'),
        (PRIVACY_TYPE.EXCEPT_SOME_FRIENDS, 'except friends lists'),
    )

    class LOCALE:
        EN = 'en'
        RU = 'ru'
    LOCALE_CHOICES = (
        (LOCALE.EN, 'English'),
        (LOCALE.RU, 'Russian'),
    )

    vk_id = models.CharField(max_length=255)
    privacy_type = models.SmallIntegerField(choices=PRIVACY_TYPE_CHOICES, default=PRIVACY_TYPE.ALL_FRIENDS)
    locale = models.CharField(choices=LOCALE_CHOICES, max_length=3, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.vk_id


class VkSession(models.Model):
    account = models.ForeignKey(Account, on_delete=models.CASCADE)
    access_token = models.CharField(max_length=255)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __unicode__(self):
        return self.account


class FriendsWhiteList(models.Model):
    owner = models.ForeignKey(Account, on_delete=models.CASCADE)
    friend_ext_id = models.CharField(max_length=255)


class FriendsBlackList(models.Model):
    owner = models.ForeignKey(Account, on_delete=models.CASCADE)
    friend_ext_id = models.CharField(max_length=255)
