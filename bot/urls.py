from django.urls import path
from . import views

app_name = 'bot'
urlpatterns = [
    path('webhook/',views.receive_message,name='infobip_webhook'),
    path('reports/<int:chama_id>/',views.bot_records,name='bot-records')
]