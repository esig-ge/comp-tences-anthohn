from django import forms

from .models import Video

# premmet de créer un formulaire basé sur le modèle Video en sélectionnant les champs spécifiés
class VideoForm(forms.ModelForm):

    class Meta:
        model = Video
        fields = ('title', 'description', 'video', 'thumbnail',)
        labels = {
            'title': 'Titre de la vidéo',
            'description': 'Description de la vidéo',
            'video': 'Fichier vidéo',
            'thumbnail': 'Image miniature',
        }