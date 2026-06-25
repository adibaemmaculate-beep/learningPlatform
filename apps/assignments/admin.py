from django.contrib import admin

from .models import Assignment, AssignmentSubmission


class SubmissionInline(admin.TabularInline):
    model = AssignmentSubmission
    extra = 0
    readonly_fields = ('submitted_at', 'is_late', 'status')


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'week', 'due_date', 'is_draft', 'grades_released', 'created_at')
    list_filter = ('is_draft', 'grades_released')
    inlines = [SubmissionInline]


@admin.register(AssignmentSubmission)
class AssignmentSubmissionAdmin(admin.ModelAdmin):
    list_display = ('assignment', 'student', 'status', 'is_late', 'score_obtained', 'submitted_at')
    list_filter = ('status', 'is_late')
