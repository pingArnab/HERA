import json
import operator

from django.http import JsonResponse
from django.shortcuts import Http404
from django.views.decorators.csrf import csrf_exempt
from Hera import settings
from pathlib import Path
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import MovieCollectionListSerializer, SingleMovieCollectionSerializer, SingleTVShowSerializer
from .serializers import TVShowEpisodeSerializer
from .serializers import MovieListSerializer, GenreListSerializer, GenreDetailsSerializer, TVShowListSerializer
from .models import Media, Video, Genre, TVShow
from .utils import Tmdb
import random
from django.db.models import Q
from functools import reduce
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import permission_classes


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
        except Video.DoesNotExist:
            return Response({'error': 'Movie not found'}, status=404)
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
    def get(self, request, filter=None, count=1, format=None):
        movies = []
        tvs = []
        if filter in ['movie', None]:
            movies = Video.objects.filter(type='M')
            movies = list(MovieListSerializer(movies, many=True).data)
            random.shuffle(movies)

        if filter == ['tv', None]:
            tvs = TVShow.objects.filter(type='T')
            tvs = list(SingleTVShowSerializer(tvs, many=True).data)
            random.shuffle(tvs)

        medias = movies + tvs
        if not medias:
            return Response({
                "error": "No results found"
            })

        return Response(medias[:count])


class RandomCollection(APIView):
    def get(self, request, format=None):
        collections = Media.objects.filter(type='M')
        serializer = SingleMovieCollectionSerializer(random.choice(collections), many=False)
        return Response(serializer.data)


class MovieList(APIView):
    def get(self, request, sort_type=None, count=None, format=None):
        movies = Video.objects.filter(type='M')
        if str(sort_type).lower().strip() == 'popular':
            sorted_movies = movies.order_by('-popularity')
        elif str(sort_type).lower().strip() == 'latest':
            sorted_movies = movies.order_by('-release_date')
        elif str(sort_type).lower().strip() == 'top-rated':
            sorted_movies = movies.order_by('-rating')
        elif str(sort_type).lower().strip() == 'newly-added':
            sorted_movies = movies.order_by('-timestamp')
        else:
            sorted_movies = movies

        serializer = MovieListSerializer(sorted_movies[:count] if count else sorted_movies, many=True)
        return Response(serializer.data)


class Search(APIView):
    def get(self, request, format=None):
        q = request.GET.get('q')
        q_list = q.split(' ')

        search_filters = []
        for key in q_list:
            search_filters.append(Q(name__icontains=key))
            search_filters.append(Q(description__icontains=key))
            if Genre.objects.filter(name__icontains=key):
                search_filters.append(Q(genre=Genre.objects.get(name__icontains=key)))

        video = Video.objects.filter(type='M').filter(reduce(operator.or_, search_filters)).order_by('-popularity')
        serializer = MovieListSerializer(video, many=True)
        return Response(serializer.data)


@permission_classes([IsAuthenticated])
class MongoDb(APIView):

    def get(self, request, format=None):
        return Response({'mongoBD': 'mongoDB'})


# ---------------------- TV SHows ----------------------
class TVList(APIView):

    def get(self, request, sort_type=None, count=None, format=None):
        tvs = TVShow.objects.all()
        if str(sort_type).lower().strip() == 'popular':
            sorted_tvs = tvs.order_by('-popularity')
        elif str(sort_type).lower().strip() == 'latest':
            sorted_tvs = tvs.order_by('-release_date')
        elif str(sort_type).lower().strip() == 'top-rated':
            sorted_tvs = tvs.order_by('-rating')
        elif str(sort_type).lower().strip() == 'newly-added':
            sorted_tvs = tvs.order_by('-timestamp')
        else:
            sorted_tvs = tvs

        serializer = TVShowListSerializer(sorted_tvs[:count] if count else sorted_tvs, many=True)
        return Response(serializer.data)


class TVDetails(APIView):
    def get(self, request, tv_id, format=None):
        try:
            tvs = TVShow.objects.get(tmdb_id=tv_id)
        except TVShow.DoesNotExist:
            return Response({'error': 'TV Show not found'}, status=404)

        seasons_list = list(tvs.video_set.values_list('season_no', flat=True).distinct())
        seasons = dict()
        for season in seasons_list:
            seasons[int(season)] = TVShowEpisodeSerializer(tvs.video_set.filter(season_no=int(season)), many=True).data

        serializer = TVShowListSerializer(tvs, many=False)
        response = dict()
        response.update(serializer.data)
        response.update({'seasons': seasons})
        return Response(response)
