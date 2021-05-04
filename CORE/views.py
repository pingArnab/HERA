import json

from django.http import JsonResponse
from django.shortcuts import Http404
from django.views.decorators.csrf import csrf_exempt
from Hera import settings
from pathlib import Path
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import MovieCollectionListSerializer, SingleMovieCollectionSerializer
from .serializers import MovieListSerializer, GenreListSerializer, GenreDetailsSerializer
from .models import Media, Video, Genre
from .utils import Tmdb
import random


# Create your views here.
@csrf_exempt
def handle_media_dirs(request):
    # Restricting the other non-supported methods
    if request.method not in ['POST', "GET"]:
        return JsonResponse({'error': 'Invalid Request'}, status=400)

    # For post updating the dir records
    if request.method == 'POST':
        body = json.loads(request.body)
        updated_dirs_list = body.get('directories')
        for index, updated_dir in enumerate(updated_dirs_list):
            if not Path(updated_dir).exists():
                return JsonResponse({'error': 'Invalid path'}, status=400)
            updated_dirs_list[index] = updated_dir.replace('\\', '\\\\')

        staticfiles_dir_file = open(settings.BASE_DIR / 'staticfiles_dirs.csv', 'w')
        staticfiles_dir_file.write(','.join(updated_dirs_list))
        staticfiles_dir_file.close()

    # Common for both get and post
    staticfiles_dir_file = open(settings.BASE_DIR / 'staticfiles_dirs.csv', 'r')
    staticfiles_dirs = list(map(lambda x: str(Path(x)), staticfiles_dir_file.read().split(',')))
    staticfiles_dir_file.close()
    return JsonResponse({'directories': staticfiles_dirs})


class MovieCollectionList(APIView):
    def get(self, request, format=None):
        movies = Media.objects.filter(type='M')
        serializer = MovieCollectionListSerializer(movies, many=True)
        return Response(serializer.data)


class MovieCollectionDetails(APIView):
    def get(self, request, movie_collection_id, format=None):
        try:
            movie_collection = Media.objects.get(tmdb_id=movie_collection_id)
        except Media.DoesNotExist:
            return Response({'error': 'Collection not found'}, status=404)
        serializer = SingleMovieCollectionSerializer(movie_collection, many=False)
        return Response(serializer.data)


class MovieDetails(APIView):
    def get(self, request, movie_id, format=None):
        try:
            movie = Video.objects.get(tmdb_id=movie_id)
        except Media.DoesNotExist:
            return Response({'error': 'Collection not found'}, status=404)
        serializer = MovieListSerializer(movie, many=False)
        return Response(serializer.data)


class GenreList(APIView):
    def get(self, request, format=None):
        genre = Genre.objects.all()
        serializer = GenreListSerializer(genre, many=True)
        return Response(serializer.data)


class GenreDetails(APIView):
    def get(self, request, genre_id, format=None):
        try:
            genre = Genre.objects.get(tmdb_id=genre_id)
        except Genre.DoesNotExist:
            return Response({'error': 'Genre not found'}, status=404)
        serializer = GenreDetailsSerializer(genre, many=False)
        return Response(serializer.data)


class RandomMedia(APIView):
    def get(self, request, format=None):
        media_list = []
        movies = Video.objects.filter(type='M')
        movies and media_list.append(MovieListSerializer(random.choice(movies), many=False).data)

        tvs = Media.objects.filter(type='S')
        tvs and media_list.append(SingleMovieCollectionSerializer(random.choice(tvs), many=False).data)

        return Response(random.choice(media_list) if media_list else {})


class MovieList(APIView):
    def get(self, request, sort_type=None, count=None, format=None):
        movies = Video.objects.filter(type='M')
        if str(sort_type).lower().strip() == 'popular':
            sorted_movies = movies.order_by('-popularity', '-rating', '-release_date', '-timestamp')
        elif str(sort_type).lower().strip() == 'latest':
            sorted_movies = movies.order_by('-release_date','-popularity',  '-rating', '-timestamp')
        elif str(sort_type).lower().strip() == 'top-rated':
            sorted_movies = movies.order_by('-rating', '-popularity', '-release_date', '-timestamp')
        elif str(sort_type).lower().strip() == 'newly-added':
            sorted_movies = movies.order_by('-timestamp', '-popularity', '-rating', '-release_date')
        else:
            sorted_movies = movies

        serializer = MovieListSerializer(sorted_movies[:count] if count else sorted_movies, many=True)
        return Response(serializer.data)
