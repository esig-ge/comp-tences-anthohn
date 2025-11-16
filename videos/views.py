from django.utils import timezone
from django.shortcuts import render
from .models import Video
from django.shortcuts import render


# Create your views here.
def video_list(request):
    videos = Video.objects.filter(uploaded_at__lte=timezone.now()).order_by('uploaded_at')
    return render(request, 'videos/video_list.html', {'videos': videos})