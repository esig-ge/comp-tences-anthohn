from django.db import models
from django.utils import timezone
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

# Fonction de validation pour la taille du fichier, taille max : 100 Mo
def validate_video_size(value):
    max_size_mb = 100
    if value.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"La taille maximale du fichier est de {max_size_mb} Mo.")

# Fonction de validation pour la taille du fichier, taille max : 5 Mo
def validate_thumbnail_size(value):
    max_size_mb = 5
    if value.size > max_size_mb * 1024 * 1024:
        raise ValidationError(f"La taille maximale du fichier est de {max_size_mb} Mo.")

# Create your models here.
class Video(models.Model):
    # Si message erreur front & back, blank=False
    title = models.CharField(max_length=50)
    # https://www.geeksforgeeks.org/python/what-is-the-max-size-of-max-length-in-django/
    # No need for max_length
    # blank=True allows the description to be optional
    # blank=False makes the field required
    # # # # # # # # # # # # # # # # #  # # 
    # par défaut, les champs sont obligatoire
    # # # # # # # # # # # # # # # # #  # # 
    description = models.TextField()
    # fichier stocké dans le dossier "videos/"
    video = models.FileField(
        upload_to='videos/',
        validators=[
            FileExtensionValidator(allowed_extensions=['mp4', 'mov', 'avi', 'mkv']),
            validate_video_size
        ]
    )
    # fichier stocké dans le dossier "thumbnails/"
    thumbnail = models.ImageField(
        upload_to='thumbnails/',
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg', 'png', 'webp']),
            validate_thumbnail_size
        ]
    )
    uploaded_at = models.DateTimeField(default=timezone.now)