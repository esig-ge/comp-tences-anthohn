from django.utils import timezone
from django.shortcuts import render
from .models import Video
from django.shortcuts import render, get_object_or_404
from .forms import VideoForm
from django.shortcuts import redirect


# Create your views here.
def video_list(request):
    videos = Video.objects.filter(uploaded_at__lte=timezone.now()).order_by('uploaded_at')
    return render(request, 'videos/video_list.html', {'videos': videos})

def video_detail(request, pk):
    video = get_object_or_404(Video, pk=pk)
    return render(request, 'videos/video_detail.html', {'video': video})

def video_new(request):
    if request.method == "POST":
        form = VideoForm(request.POST)
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
        form = VideoForm(request.POST, instance=video)
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
        video.delete()
        return redirect('video_list')
    
    # Si la requête n'est pas de type POST, redirige vers la liste des vidéos
    # Si quelqu'un essaie d'accéder directement à cette vue via GET, on ne supprime pas la vidéo et on redirige simplement
    return redirect('video_list')