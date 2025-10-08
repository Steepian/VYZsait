from django.db import models


class University(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    location = models.CharField(max_length=255)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to="university_logos/", blank=True)
    rating = models.FloatField(default=0.0)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ["name"]

