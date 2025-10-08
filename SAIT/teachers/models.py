from django.db import models
from users.models import CustomUser
from universities.models import University


class Teacher(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    university = models.ForeignKey(University, on_delete=models.SET_NULL, null=True)
    position = models.CharField(max_length=255)
    department = models.CharField(max_length=255)
    rating = models.FloatField(default=0.0)

    def __str__(self):
        return f"{self.user.get_full_name()} - {self.position}"

    class Meta:
        ordering = ["user__last_name"]
