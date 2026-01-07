from django.urls import path
from . import views

urlpatterns = [
    path('', views.video_list, name='video_list'),
    path('video/<int:pk>/', views.video_detail, name='video_detail'),
    path('video/<int:pk>/summary/', views.generate_summary, name='generate_summary'),
    path('video/new/', views.video_new, name='video_new'),
    path('video/<int:pk>/edit/', views.video_edit, name='video_edit'),
    path('video/<int:pk>/delete/', views.video_delete, name='video_delete'),
    path('search/', views.search_videos, name='search_videos'),
]