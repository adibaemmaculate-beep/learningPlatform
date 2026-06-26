import re
import uuid

from django.conf import settings
from django.db import models


class Update(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(help_text='Markdown content')
    cover_image = models.ImageField(upload_to='updates/covers/', blank=True, null=True)
    cover_image_caption = models.CharField(max_length=500, blank=True)
    author_name = models.CharField(max_length=255, blank=True)
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

    @property
    def cover_image_url(self):
        if self.cover_image:
            return self.cover_image.url
        return None

    @property
    def display_author(self):
        if self.author_name and self.author_name.strip():
            return self.author_name.strip()
        if self.writer:
            return self.writer.get_full_name()
        return 'Shamva Innovators'

    def excerpt(self, length=150):
        text = self.description or ''
        text = re.sub(r'<figure[^>]*>.*?</figure>', '', text, flags=re.DOTALL | re.IGNORECASE)
        text = re.sub(r'<[^>]+>', '', text)
        text = re.sub(r'!\[([^\]]*)\]\([^)]+\)', r'\1', text)
        text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', text)
        text = re.sub(r'#{1,6}\s*', '', text)
        text = re.sub(r'[*_~`>|]', '', text)
        text = text.replace('\n', ' ')
        text = re.sub(r'\s+', ' ', text).strip()
        if len(text) > length:
            return text[:length].rsplit(' ', 1)[0] + '...'
        return text
