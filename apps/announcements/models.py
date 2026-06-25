import uuid

from django.conf import settings
from django.db import models
from django.utils import timezone


class Announcement(models.Model):
    class Visibility(models.TextChoices):
        EVERYONE = 'everyone', 'Everyone'
        STUDENTS_ONLY = 'students_only', 'Students only'
        TEACHERS_ONLY = 'teachers_only', 'Teachers only'
        SPECIFIC_STUDENT = 'specific_student', 'Specific student'

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    body = models.TextField()
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='announcements_created'
    )
    visibility = models.CharField(max_length=20, choices=Visibility.choices, default=Visibility.EVERYONE)
    target_student = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, null=True, blank=True,
        related_name='targeted_announcements',
    )
    published_at = models.DateTimeField(default=timezone.now)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_at']

    def __str__(self):
        return self.title

    def read_count(self):
        return self.reads.count()


class AnnouncementRead(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='reads')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='announcement_reads')
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['announcement', 'user']]

    def __str__(self):
        return f'{self.user} read {self.announcement.title}'
