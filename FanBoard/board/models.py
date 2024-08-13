from django.conf import settings
from django.db import models
from ckeditor.fields import RichTextField


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


class Response(models.Model):
    post = models.ForeignKey(Post, related_name='responses', on_delete=models.CASCADE)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    response_time = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        return f'Отзыв от {self.author} на {self.post}'
