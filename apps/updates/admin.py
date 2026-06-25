from django.contrib import admin

from .models import Update


@admin.register(Update)
class UpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'writer', 'published_at', 'created_at')
    list_filter = ('published_at',)
    search_fields = ('title', 'description')
