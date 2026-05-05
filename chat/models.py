from django.db import models
from django.contrib.auth.models import User


class Room(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name='Назва')
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True, verbose_name='Опис')
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='created_rooms'
    )

    class Meta:
        verbose_name = 'Кімната'
        verbose_name_plural = 'Кімнати'
        ordering = ['name']

    def __str__(self):
        return self.name

    def get_last_messages(self, count=50):
        return self.messages.select_related('author').order_by('-created_at')[:count][::-1]


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='messages')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='messages')
    content = models.TextField(verbose_name='Повідомлення')
    created_at = models.DateTimeField(auto_now_add=True)
    is_deleted = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Повідомлення'
        verbose_name_plural = 'Повідомлення'
        ordering = ['created_at']

    def __str__(self):
        return f'{self.author.username}: {self.content[:40]}'
