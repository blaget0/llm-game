"""
URL configuration for ArenaAI project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.urls import path
from gameAI.views import index, TEST_DRAW, home_page, drawing_board, save_drawing, register_view, login_view, logout_view
from gameAI.views import game_history, leaderbord

urlpatterns = [
    path('register/', register_view),
    path('accounts/login/', login_view),
    path("admin", admin.site.urls),
    path('', home_page, name='home'),
    path("game", index),
    path("draw", drawing_board),
    path('save_drawing/', save_drawing),
    path('TEST', TEST_DRAW),
    path('history', game_history, name='history'),
    path('logout', logout_view),
    path('leaderbord', leaderbord)
]
from django.conf import settings
from django.conf.urls.static import static


if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
