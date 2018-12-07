from django.contrib import admin

from .models import Account, VkSession


class AccountAdmin(admin.ModelAdmin):
    list_display = ('vk_id', 'created_at')
    search_fields = ('vk_id', )


class VkSessionAdmin(admin.ModelAdmin):
    list_display = ('account_vk', 'access_token', 'expires_at')
    raw_id_fields = ('account', )
    search_fields = ('account__vk_id', )

    def account_vk(self, obj):
        return obj.account.vk_id
    account_vk.short_description = "VK id"


admin.site.register(Account, AccountAdmin)
admin.site.register(VkSession, VkSessionAdmin)