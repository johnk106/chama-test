from django.http import JsonResponse
from django.urls import path
from . import views


urlpatterns=[
path('distribute_chama_bi_weekly/', views.distribute_chama_bi_weekly, name='distribute_chama_bi_weekly'),
path('distribute_chama_weekly/', views.distribute_chama_weekly, name='distribute_chama_weekly'),
path('distribute_chama_monthly/', views.distribute_chama_monthly, name='distribute_chama_monthly'),
path('contribution_alert_biweekly/', views.contribution_alert_biweekly, name='contribution_alert_biweekly'),
path('contribution_alert_weekly/', views.contribution_alert_weekly, name='contribution_alert_weekly'),
path('contribution_alert_monthly/', views.contribution_alert_monthly, name='contribution_alert_monthly'),
path('end_chamas_life_completes/', views.end_chamas_life_completes, name='end_chamas_life_completes'),


#goals alerts
path('goal_contribution_alert/', views.goal_contribution_alert, name='goal_contribution_alert'),

path('wallet_index/', views.wallet_index, name='wallet_index'),




]