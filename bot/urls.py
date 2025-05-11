from django.urls import path
from . import views

app_name = 'bot'
urlpatterns = [
    path('webhook/',views.receive_message,name='infobip_webhook'),
    path('reports/<int:chama_id>/',views.bot_records,name='bot-records'),
    path('contributions/approve/<int:chama_id>/',views.approve_contribution,name='approve-contribution'),
    path('loans/approve/<int:chama_id>/',views.approve_loan,name='approve-loan'),
    path('fines/approve/<int:chama_id>/',views.approve_fine,name='approve-fine')
]