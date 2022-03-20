from django.urls import path

from . import views

app_name = 'polls'
urlpatterns = [
    path('v1/health/', views.health),
    path('v2/patches/', views.patches),
]
