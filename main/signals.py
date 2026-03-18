from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Review
from django.db.models import Avg

@receiver([post_save, post_delete], sender=Review)
def update_university_rating(sender, instance, **kwargs):
    """Пересчитывает рейтинг университета при сохранении/удалении отзыва"""
    instance.university.update_rating()