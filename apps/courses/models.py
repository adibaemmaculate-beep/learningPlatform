import uuid

from django.db import models


class Course(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


def slides_upload_path(instance, filename):
    return f'materials/slides/{instance.id}/{filename}'


def notes_upload_path(instance, filename):
    return f'materials/notes/{instance.id}/{filename}'


class CourseMaterial(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='materials')
    week = models.PositiveIntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    objectives_json = models.JSONField(default=list, blank=True)
    slides = models.FileField(upload_to=slides_upload_path, blank=True, null=True)
    notes = models.FileField(upload_to=notes_upload_path, blank=True, null=True)
    other_resources_json = models.JSONField(default=list, blank=True)
    published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['week']
        unique_together = [['course', 'week']]

    def __str__(self):
        return f'Week {self.week}: {self.title}'
