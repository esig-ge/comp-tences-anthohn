from django.utils import timezone
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Video
from .forms import VideoForm
from django.http import JsonResponse
import os
import time
import google.generativeai as genai

api_key = os.getenv("GOOGLE_API_KEY")
genai.configure(api_key=api_key)


# Create your views here.
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

from django.contrib import messages     # Ajouter cet import en haut du fichier si pas déjà présent (je le ferai dans un autre bloc si besoin, mais ici je modifie generate_summary)

def generate_summary(request, pk):
    """
    Vue pour générer un résumé automatique de la vidéo via Gemini.
    Utilise gemini-flash-latest pour un meilleur équilibre vitesse/quota.
    """
    video_instance = get_object_or_404(Video, pk=pk)

    try:
        # 1. Upload du fichier vers l'API Gemini
        print(f"Début de l'upload pour : {video_instance.title}")
        video_file = genai.upload_file(path=video_instance.video.path)

        # 2. Attente de la fin du traitement
        while video_file.state.name == "PROCESSING":
            print("Traitement de la vidéo par l'IA en cours...")
            time.sleep(5)
            video_file = genai.get_file(video_file.name)

        if video_file.state.name == "FAILED":
            raise Exception("L'indexation de la vidéo a échoué sur les serveurs Gemini.")

        # 3. Initialisation du modèle
        # On utilise gemini-flash-latest qui est souvent plus permissif sur les quotas free-tier
        model = genai.GenerativeModel(model_name="gemini-flash-latest")
        prompt = (
            "Analyse cette vidéo et fais-en un résumé structuré en français. "
            "Identifie le sujet principal et les points clés abordés. "
            "Sois concis."
        )

        # Génération du contenu
        response = model.generate_content([video_file, prompt])

        # 4. Sauvegarde
        video_instance.summary = response.text
        video_instance.save()
        messages.success(request, "Résumé généré avec succès !")
        print("Résumé généré et sauvegardé avec succès.")

    except Exception as e:
        error_msg = f"Erreur lors de la génération : {str(e)}"
        print(error_msg)
        # Affiche un message d'erreur à l'utilisateur
        messages.error(request, "Une erreur est survenue lors de la génération du résumé. Vérifiez les quotas ou réessayez plus tard.")

    # 5. Redirection
    return redirect('video_detail', pk=pk)