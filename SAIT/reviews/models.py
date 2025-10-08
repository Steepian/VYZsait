from django.db import models
from users.models import CustomUser
from universities.models import University
from teachers.models import Teacher


class Review(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.SET_NULL, null=True)
    teacher = models.ForeignKey(Teacher, on_delete=models.SET_NULL, null=True)
    text = models.TextField()
    rating = models.FloatField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Отзыв от {self.user.username} о {self.teacher or self.university}"

    class Meta:
        ordering = ["-created_at"]
