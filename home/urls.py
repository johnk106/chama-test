from django.urls import path
from . import views


urlpatterns=[
path('', views.Home, name='index'),
path('homepage', views.homepage, name='homepage'),
path('term_conditions', views.term_conditions, name='term_conditions'),
path('privacy_policies', views.privacy_policies, name='privacy_policies'),
]