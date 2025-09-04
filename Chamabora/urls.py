"""Chamabora URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from authentication.views import showFirebaseJS

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('user/', include('authentication.urls')),
    path('wallet/', include('wallet.urls')),
    path('homepage/', include('Goals.urls')),
    path('load_money/', include('mpesa_integration.urls')),
    path('withdraw/', include('pyment_withdraw.urls')),
    path('dashboard/', include('Dashboard.urls')),
    path('notifications/', include('notifications.urls')),
    path('send/', include('notifications.urls')),
    path('firebase-messaging-sw.js', showFirebaseJS, name="show_firebase_js"),
    path('subscriptions/', include('subscriptions.urls')),
    path('chamas-bookeeping/',include('chamas.urls')),
    path('bot/',include('bot.urls'))
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
