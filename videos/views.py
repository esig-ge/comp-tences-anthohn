from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Video
from .forms import VideoForm
from django.http import JsonResponse
# os permet de récupérer des variables d'environnement
import os
# time permet de gérer des délais
import time
# google.genai is the new official SDK
from google import genai
# messages permet d'afficher des messages dans la page
from django.contrib import messages

api_key = os.getenv("GOOGLE_API_KEY")

# Create your views here.
def process_video_summary(video_instance):
    """
    Fonction utilitaire pour générer le résumé via Gemini (SDK google-genai).
    """
    client = genai.Client(api_key=api_key)

    print(f"Début de l'upload pour : {video_instance.title}")

    # Upload de la vidéo via le nouveau SDK
    # on utilise l'argument 'file' pour le chemin du fichier
    video_file = client.files.upload(file=video_instance.video.path)

    # Attente de la fin du traitement
    while video_file.state.name == "PROCESSING":
        time.sleep(5)
        # On rafraîchit l'objet fichier
        video_file = client.files.get(name=video_file.name)

    if video_file.state.name == "FAILED":
        raise Exception("L'indexation de la vidéo a échoué sur les serveurs Gemini.")

    # Prompt pour Gemini Flash
    prompt = (
        "Analyse cette vidéo et fais-en un résumé structuré en français. "
        "Identifie le sujet principal et les points clés abordés. "
        "Sois concis."
    )

    # Génération du contenu avec le nouveau client
    # On utilise "gemini-1.5-flash" qui est le nom standard actuel
    response = client.models.generate_content(
        model="gemini-1.5-flash",
        contents=[video_file, prompt]
    )

    # Sauvegarde
    video_instance.summary = response.text
    video_instance.save()

def video_list(request):
    videos = Video.objects.filter(uploaded_at__lte=timezone.now()).order_by('uploaded_at')
    return render(request, 'videos/video_list.html', {'videos': videos})

def video_detail(request, pk):
    video = get_object_or_404(Video, pk=pk)
    return render(request, 'videos/video_detail.html', {'video': video})

def video_new(request):
    if request.method == "POST":
        # ajout de request.FILES pour gérer les fichiers uploadés
        form = VideoForm(request.POST, request.FILES)
        if form.is_valid():
            video = form.save(commit=False)
            video.author = request.user
            video.published_date = timezone.now()
            video.save()

            # Génération automatique du résumé après l'upload de la vidéo
            try:
                # appel de la fonction process_video_summary
                process_video_summary(video)
                # message de succès
                messages.success(request, "Vidéo ajoutée et résumé généré avec succès !")
            except Exception as e:
                # message d'erreur
                messages.warning(request, "Vidéo ajoutée, mais le résumé n'a pas pu être généré automatiquement. Vous pouvez réessayer depuis la page de détails.")

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


def generate_summary(request, pk):
    """
    Vue pour générer un résumé automatique de la vidéo via Gemini.
    Utilise gemini-flash-latest pour un meilleur équilibre vitesse/quota.
    """
    video_instance = get_object_or_404(Video, pk=pk)

    try:
        process_video_summary(video_instance)
        messages.success(request, "Résumé généré avec succès !")

    except Exception as e:
        error_msg = f"Erreur lors de la génération : {str(e)}"
        print(error_msg)
        messages.error(request, "Une erreur est survenue lors de la génération du résumé. Vérifiez les quotas ou réessayez plus tard.")

    # 5. Redirection
    return redirect('video_detail', pk=pk)