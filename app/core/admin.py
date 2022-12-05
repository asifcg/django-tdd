"""
Register models for admin site
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from core import models


class UserAdmin(BaseUserAdmin):
    """Admin for User model."""
    ordering = ['id']
    list_display = ['name', 'email', 'is_active', 'is_staff', 'is_superuser']
    list_display_links = ['name', 'email']
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('name',)}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login',)})
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('name', 'email', 'password1', 'password2')
        }),
    )
    readonly_fields = ('last_login',)


admin.site.register(models.User, UserAdmin)
