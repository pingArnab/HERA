from django.urls import path
from . import views

urlpatterns = [
    path('sync/', views.Sync.as_view()),
]
