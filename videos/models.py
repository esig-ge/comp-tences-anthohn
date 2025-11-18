from django.db import models
from django.utils import timezone

# Create your models here.
class Video(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    # fichier stocké dans le dossier "videos/"
    video = models.FileField(upload_to='videos/')
    # fichier stocké dans le dossier "thumbnails/"
    thumbnail = models.ImageField(upload_to='thumbnails/')
    uploaded_at = models.DateTimeField(default=timezone.now)