from django.contrib import admin

from .models import Project, ProjectImage


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 0


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('title', 'student', 'is_published', 'updated_at')
    list_filter = ('is_published',)
    search_fields = ('title', 'student__email', 'student__first_name', 'student__last_name')
    inlines = [ProjectImageInline]
