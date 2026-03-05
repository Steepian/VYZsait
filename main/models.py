from django.db import models
from django.contrib.auth.models import User

class University(models.Model):
    """Модель университета"""
    name = models.CharField(
        max_length=255,
        verbose_name='Название вуза'
    )
    description = models.TextField(
        verbose_name='Описание',
        blank=True,  # может быть пустым
        help_text='Краткое описание университета'
    )
    city = models.CharField(
        max_length=100,
        verbose_name='Город'
    )
    website = models.URLField(
        max_length=255,
        verbose_name='Официальный сайт',
        blank=True,  # необязательное поле
        null=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата обновления'
    )

    class Meta:
        verbose_name = 'Университет'
        verbose_name_plural = 'Университеты'
        ordering = ['-created_at']  # сортировка по умолчанию: новые сверху

    def __str__(self):
        return self.name


class Review(models.Model):
    RATING_CHOICES = [
        (1, '1 - Ужасно'),
        (2, '2 - Плохо'),
        (3, '3 - Нормально'),
        (4, '4 - Хорошо'),
        (5, '5 - Отлично'),
    ]

    university = models.ForeignKey(
        University,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Университет'
    )
    # Вместо author_name:
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name='Автор',
        null=True,  # временно разрешаем NULL, чтобы можно было применить миграцию
        blank=True
    )
    text = models.TextField(verbose_name='Текст отзыва')
    rating = models.IntegerField(choices=RATING_CHOICES, verbose_name='Оценка')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата отзыва')
    moderated = models.BooleanField(default=False, verbose_name='Прошел модерацию')

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ['-created_at']

    def __str__(self):
        return f'Отзыв от {self.author.username if self.author else "Аноним"} о {self.university.name}'
