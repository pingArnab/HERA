import json

from django.http import JsonResponse
from django.shortcuts import Http404
from django.views.decorators.csrf import csrf_exempt
from Hera import settings
from pathlib import Path
from rest_framework.views import APIView
from rest_framework.response import Response
from .serializers import MovieCollectionListSerializer, SingleMovieCollectionSerializer, MovieDetailsSerializer
from .models import Media, Video
from .utils import Tmdb


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
        serializer = MovieDetailsSerializer(movie, many=False)
        return Response(serializer.data)

