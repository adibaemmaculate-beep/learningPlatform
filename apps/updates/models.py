import uuid

from django.conf import settings
from django.db import models


class Update(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(help_text='Markdown content')
    images_json = models.JSONField(default=list, blank=True)
    writer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, related_name='updates'
    )
    published_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-published_at', '-created_at']

    def __str__(self):
        return self.title

    @property
    def is_published(self):
        return self.published_at is not None

    def excerpt(self, length=150):
        text = self.description.replace('\n', ' ')
        return text[:length] + '...' if len(text) > length else text
