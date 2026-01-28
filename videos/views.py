from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from .models import Video
from .forms import VideoForm
from django.http import JsonResponse


# FIXE 
from datetime import timedelta
from django.core.exceptions import PermissionDenied

# Create your views here.
def video_list(request):
    videos = Video.objects.filter(uploaded_at__lte=timezone.now()).order_by('uploaded_at')
    return render(request, 'videos/video_list.html', {'videos': videos})

def video_detail(request, pk):
    video = get_object_or_404(Video, pk=pk)
    return render(request, 'videos/video_detail.html', {'video': video})

def video_new(request):
    if request.method == "POST":

        ######### FIXE : pour empêcher le spam #########
        # timezone.now sert à obtenir la date et l'heure actuelles et timedelta sert à obtenir la date et l'heure actuelles moins 10 minutes
        dix_min_ago = timezone.now() - timedelta(minutes=10)
        # Video.objects.filter sert à obtenir toutes les vidéos qui ont été uploadées par l'utilisateur et qui ont été uploadées il y a moins de 10 minutes
        user_uploads = Video.objects.filter(author=request.user, uploaded_at__gte=dix_min_ago).count()

        # Si l'utilisateur a uploadé 3 vidéos ou plus il y a moins de 10 minutes, on retourne une erreur 403
        if user_uploads >= 3:
            # retourne une erreur 403
            raise PermissionDenied("Alerte Spam : Trop d'uploads en peu de temps.")
        ################################################


        # ajout de request.FILES pour gérer les fichiers uploadés
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.author = request.user
            video.published_date = timezone.now()
            video.save()
            return redirect('video_detail', pk=video.pk)
    else:
        form = VideoForm()
    return render(request, 'videos/video_edit.html', {'form': form})

def video_edit(request, pk):
    video = get_object_or_404(Video, pk=pk)
    if request.method == "POST":
        # ajout de request.FILES pour gérer les fichiers uploadés
        form = VideoForm(request.POST, request.FILES, instance=video)
        if form.is_valid():
            # le commit=False permet d'enregister les données présentent dans le forms.py sans les sauvegarder directement en base de données et en attendant d'ajouter d'autres informations
            video = form.save(commit=False)
            video.author = request.user
            video.published_date = timezone.now()
            video.save()
            return redirect('video_detail', pk=video.pk)
    else:
        form = VideoForm(instance=video)
    return render(request, 'videos/video_edit.html', {'form': form})

def video_delete(request, pk):
    # dangeureux : Si pk n'existe pas, le serveur plante
    # video = Video.objects.get(pk=pk)

    # Récupère l'objet vidéo à supprimer ou renvoie une erreur 404 si elle n'existe pas
    video = get_object_or_404(Video, pk=pk)
    
    # Passe par ici uniquement si la requête est de type POST
    if request.method == "POST":

        ######### FIXE : pour supprimer le fichier vidéo et le fichier de miniature #########
        # Sans se fixe, le fichier vidéo et le fichier de miniature ne sont pas supprimés 
        # Sans save=False : Django ferait 3 requêtes à la base de données (Update vidéo, Update miniature, puis Delete de la ligne). C'est inutile de mettre à jour une ligne que tu vas supprimer la seconde d'après !
        # Avec save=False : Django supprime les fichiers sur le disque,
        # mais ne perd pas de temps à modifier la base de données.
        # Il attend le video.delete() final pour tout nettoyer d'un coup.
        if video.video:
            video.video.delete(save=False) # Supprime le MP4
            
        if video.thumbnail:
            video.thumbnail.delete(save=False) # Supprime le JPG/PNG
        ################################################

        video.delete()
        return redirect('video_list')
    
    # Si la requête n'est pas de type POST, redirige vers la liste des vidéos
    # Si quelqu'un essaie d'accéder directement à cette vue via GET, on ne supprime pas la vidéo et on redirige simplement
    return redirect('video_list')

def search_videos(request):
    query = request.GET.get('q', '')
    if query:
        # Recherche insensible à la casse (icontains)
        videos = Video.objects.filter(title__icontains=query)[:5]
        results = [{'id': video.id, 'title': video.title} for video in videos]
    else:
        results = []
    return JsonResponse(results, safe=False)
