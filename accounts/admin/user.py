from django.contrib import admin

from accounts.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("username", "email", "first_name", "last_name", "tin", "balance")
    search_fields = ("username", "email", "first_name", "last_name", "tin")
    ordering = ("-id",)
