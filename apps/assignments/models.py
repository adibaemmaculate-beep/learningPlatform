import uuid

from django.conf import settings
from django.db import models

from apps.courses.models import Course


def submission_upload_path(instance, filename):
    return f'submissions/{instance.assignment_id}/{instance.student_id}/{filename}'


class Assignment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=255)
    instructions = models.TextField(blank=True)
    week = models.PositiveIntegerField()
    due_date = models.DateTimeField()
    total_score = models.PositiveIntegerField(default=100)
    allowed_file_types = models.JSONField(default=list)
    max_file_size_mb = models.PositiveIntegerField(default=10)
    grades_released = models.BooleanField(default=False)
    is_draft = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='created_assignments'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['due_date', 'week']

    def __str__(self):
        return self.title

    @property
    def is_published(self):
        return not self.is_draft

    def submission_count(self):
        return self.submissions.count()

    def class_size(self):
        from apps.accounts.models import User
        return User.objects.filter(type=User.UserType.STUDENT, status=User.UserStatus.ACTIVE).count()


class AssignmentSubmission(models.Model):
    class Status(models.TextChoices):
        SUBMITTED = 'submitted', 'Submitted'
        GRADED = 'graded', 'Graded'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='assignment_submissions'
    )
    file = models.FileField(upload_to=submission_upload_path)
    file_name = models.CharField(max_length=255)
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_late = models.BooleanField(default=False)
    score_obtained = models.PositiveIntegerField(null=True, blank=True)
    comments = models.TextField(blank=True)
    graded_at = models.DateTimeField(null=True, blank=True)
    graded_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name='graded_submissions'
    )
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.SUBMITTED)

    class Meta:
        unique_together = [['assignment', 'student']]
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.student} — {self.assignment.title}'

    def save(self, *args, **kwargs):
        if self.file and not self.file_name:
            self.file_name = self.file.name.split('/')[-1]
        super().save(*args, **kwargs)
