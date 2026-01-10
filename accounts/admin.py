import admin_thumbnails
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from accounts.models import Account, UserProfile


# show the avatar image
@admin_thumbnails.thumbnail("avatar")
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = "Profiles"


@admin.register(Account)
class AccountAdmin(UserAdmin):
    list_display = (
        "first_name",
        "last_name",
        "email",
        "username",
        "last_login",
        "is_active",
        "date_joined",
    )

    list_display_links = ("email", "first_name", "last_name")
    inlines = [UserProfileInline]
    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
