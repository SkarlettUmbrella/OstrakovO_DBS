from django.urls import path
from . import views

urlpatterns = [
    path('', views.homepage, name='Home'),

    path('v1/health/', views.health),
]