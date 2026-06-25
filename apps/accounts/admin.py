from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import EmailVerificationToken, InviteCode, PasswordResetToken, User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('email', 'first_name', 'last_name', 'type', 'status', 'email_verified')
    list_filter = ('type', 'status', 'email_verified')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal', {'fields': ('first_name', 'last_name', 'phone_number')}),
        ('Account', {'fields': ('type', 'status', 'email_verified', 'email_verified_at', 'approved_at', 'approved_by')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'first_name', 'last_name', 'type', 'password1', 'password2'),
        }),
    )


@admin.register(InviteCode)
class InviteCodeAdmin(admin.ModelAdmin):
    list_display = ('code', 'role', 'status', 'expires_at', 'used_by', 'created_at')
    list_filter = ('role', 'status')
    search_fields = ('code',)


admin.site.register(EmailVerificationToken)
admin.site.register(PasswordResetToken)
