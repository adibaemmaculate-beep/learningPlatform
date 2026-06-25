import os
import uuid

from django.conf import settings
from django.db import models


def project_image_upload_path(instance, filename):
    ext = os.path.splitext(filename)[1]
    return f'projects/{instance.project.student_id}/{uuid.uuid4().hex}{ext}'


class ProjectImage(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to=project_image_upload_path)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Image for {self.project}'


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    student = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='project'
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    write_up = models.TextField(blank=True)
    codebase_url = models.URLField(blank=True, max_length=500)
    live_url = models.URLField(blank=True, max_length=500)
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-updated_at']

    def __str__(self):
        return self.title

    @property
    def image_urls(self):
        return [img.image.url for img in self.images.all()]
