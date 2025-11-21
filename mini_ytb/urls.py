"""
URL configuration for mini_ytb project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('videos.urls')),
]
# permmet en dev de servir les fichiers media
# Pourquoi c’est présent / utile

# Développement : pratique et rapide — pas besoin de config serveur (nginx/Apache) pour voir les images/vidéos que tu uploades.
# Sécurité/perf : c’est uniquement pour le développement ; ce n’est pas optimisé ni sécurisé pour la production.
# Peux‑tu t’en passer ?

# En développement : tu peux t’en passer, mais alors runserver n’affichera plus les fichiers médias (tes miniatures/vidéos n’apparaîtront plus). Ce n’est donc pas pratique sauf si tu as une autre solution locale pour servir media.
# En production : oui, tu DOIS t’en passer — et mettre en place une solution adaptée (webserver ou stockage cloud). Le bloc est entouré par if settings.DEBUG: exactement pour ça : ne pas l’utiliser en prod.
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)