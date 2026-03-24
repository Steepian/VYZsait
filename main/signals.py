from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Review, FacultyReview, TeacherReview
from django.db.models import Avg

@receiver([post_save, post_delete], sender=Review)
def update_university_rating(sender, instance, **kwargs):
    """Пересчитывает рейтинг университета при сохранении/удалении отзыва"""
    instance.university.update_rating()

@receiver([post_save, post_delete], sender=FacultyReview)
def update_faculty_rating(sender, instance, **kwargs):
    instance.faculty.update_rating()

@receiver([post_save, post_delete], sender=TeacherReview)
def update_teacher_rating(sender, instance, **kwargs):
    instance.teacher.update_rating()