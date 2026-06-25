from django.contrib import admin

from .models import Course, CourseMaterial


class CourseMaterialInline(admin.TabularInline):
    model = CourseMaterial
    extra = 0


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ('name', 'is_active')
    inlines = [CourseMaterialInline]


@admin.register(CourseMaterial)
class CourseMaterialAdmin(admin.ModelAdmin):
    list_display = ('week', 'title', 'course', 'published', 'created_at')
    list_filter = ('published', 'course')
