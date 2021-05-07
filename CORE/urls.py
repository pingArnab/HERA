from django.urls import path
from . import views

urlpatterns = [

    path('media-folders/', views.handle_media_dirs),
    path('movie-collection-list/', views.MovieCollectionList.as_view()),
    path('movie-collection/<str:movie_collection_id>/', views.MovieCollectionDetails.as_view()),
    path('random-media/', views.RandomMedia.as_view()),
    path('movie/<str:movie_id>/', views.MovieDetails.as_view()),
    path('movies/', views.MovieList.as_view()),
    path('movies/<int:count>/', views.MovieList.as_view()),
    path('movies/<str:sort_type>/', views.MovieList.as_view()),
    path('movies/<str:sort_type>/<int:count>/', views.MovieList.as_view()),
    path('genre/', views.GenreList.as_view()),
    path('genre/<str:genre_id>/', views.GenreDetails.as_view()),
    path('random-media/', views.RandomMedia.as_view()),

    path('search/', views.Search.as_view()),


    path('mongodb/', views.MongoDb.as_view()),
]
