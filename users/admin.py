from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User, ConfirmEmailToken, Loves


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('first_name', 'last_name', 'gender', 'avatar', 'latitude', 'longitude')}),
        ('Permissions', {
            'fields': ('is_active', 'is_superuser'),
        }),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')


@admin.register(ConfirmEmailToken)
class ConfirmEmailTokenAdmin(admin.ModelAdmin):
    list_display = ('user', 'key', 'created_at',)


@admin.register(Loves)
class LovesUserAdmin(admin.ModelAdmin):
    model = Loves
    list_display = ('id_to', 'id_from')