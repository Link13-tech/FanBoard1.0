import re

from django.conf import settings
from django.db import models
from ckeditor.fields import RichTextField
from django.utils.safestring import mark_safe


class Post(models.Model):
    CATEGORY_CHOICES = [
        ('TANK', 'Танки'),
        ('HEALER', 'Хилы'),
        ('DPS', 'ДД'),
        ('TRADER', 'Торговцы'),
        ('GUILDMASTER', 'Гилдмастеры'),
        ('QUESTGIVER', 'Квестгиверы'),
        ('BLACKSMITH', 'Кузнецы'),
        ('LEATHERWORKER', 'Кожевники'),
        ('ALCHEMIST', 'Зельевары'),
        ('SPELLMASTER', 'Мастера заклинаний'),
    ]

    title = models.CharField(max_length=150)
    content = RichTextField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    post_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def get_media(self):
        content = mark_safe(self.content)
        images = re.findall(r'<img[^>]+src="([^"]+)"', content)
        videos = re.findall(r'<video[^>]*src="([^"]+)"', content)
        return images, videos

    def get_first_image(self):
        images, _ = self.get_media()
        return images[0] if images else None

    def get_first_video(self):
        _, videos = self.get_media()
        return videos[0] if videos else None

    def get_content_excerpt(self):
        content = mark_safe(self.content)
        if self.get_first_image():
            return content[15000:]  # Оставить содержимое после первого изображения
        return content


class Response(models.Model):
    post = models.ForeignKey(Post, related_name='responses', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    response_time = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f'Отзыв от {self.author} на {self.post}'
