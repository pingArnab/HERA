from django.urls import path
from . import views

urlpatterns = [

    path('media-folders/', views.handle_media_dirs),
    path('movie-collection-list/', views.MovieCollectionList.as_view()),
    path('movie-collection/<str:movie_collection_id>/', views.MovieCollectionDetails.as_view()),
    path('movie/<str:movie_id>/', views.MovieDetails.as_view()),
]
