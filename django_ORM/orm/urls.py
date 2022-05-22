from . import views
from django.urls import path

urlpatterns = [
    path('v1/health/', views.health),
    path('v2/patches/', views.patches),
    path('v3/matches/<str:id>/top_purchases/', views.matches),
    path('v3/statistics/tower_kills/', views.towerkills),
]