from django.db import models
from django.utils import timezone

# Create your models here.
class Video(models.Model):
    title = models.CharField(max_length=50)
    # https://www.geeksforgeeks.org/python/what-is-the-max-size-of-max-length-in-django/
     # No need for max_length
    description = models.TextField()
    # fichier stocké dans le dossier "videos/"
    video = models.FileField(upload_to='videos/')
    # fichier stocké dans le dossier "thumbnails/"
    thumbnail = models.ImageField(upload_to='thumbnails/', max_length=255, blank=True, null=True)
    uploaded_at = models.DateTimeField(default=timezone.now)