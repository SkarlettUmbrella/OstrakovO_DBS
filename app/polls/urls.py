from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('v1/health/', views.health),
    path('v2/patches/', views.patches),
    path('v3/matches/<str:id>/top_purchases', views.matches),
    #path('v3/abilities/<str:ability_id>/usage, views.abilities'),
]
