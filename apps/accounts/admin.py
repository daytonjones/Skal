from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = BaseUserAdmin.list_display + ('is_approved',)
    list_filter = BaseUserAdmin.list_filter + ('is_approved',)
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Profile extras", {"fields": ("avatar", "theme", "is_approved")}),
    )

