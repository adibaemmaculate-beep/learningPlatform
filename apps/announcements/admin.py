from django.contrib import admin

from .models import Announcement, AnnouncementRead


@admin.register(Announcement)
class AnnouncementAdmin(admin.ModelAdmin):
    list_display = ('title', 'visibility', 'created_by', 'published_at', 'read_count')
    list_filter = ('visibility',)
    search_fields = ('title', 'body')


@admin.register(AnnouncementRead)
class AnnouncementReadAdmin(admin.ModelAdmin):
    list_display = ('announcement', 'user', 'read_at')
