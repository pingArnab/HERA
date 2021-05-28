import json
import re
from django.http import JsonResponse
from rest_framework.decorators import api_view

from Hera import settings
from pathlib import Path
from django.views.decorators.csrf import csrf_exempt
from rest_framework.response import Response
from rest_framework.views import APIView
from . import utils


class Sync(APIView):
    def get(self, request, format=None):
        tmdbapi = utils.TMDBAPI()
        movies = utils.get_all_movie_file_stat()
        for movie_name, details in movies.items():
            movie_search_key = re.compile('[\w ]*').match(movie_name).group()
            response = tmdbapi.search_movie(movie_search_key).json()
            if response.get("results"):
                movies[movie_name]['tmdb_id'] = response["results"][0]["id"]
                movies[movie_name]['title'] = response["results"][0]["original_title"]
                sync_status = utils.add_movie_to_db(
                    tmdbapi.get_movie_by_id(response["results"][0]["id"]),
                    movie_name,
                    details.get('media_dir_hash')
                )
                movies[movie_name]['sync_status'] = sync_status

        tvs = utils.get_all_tv_show_file_stat()
        for tv_show_name, details in tvs.items():
            tv_search_key = re.compile('[\w ]*').match(tv_show_name).group()
            response = tmdbapi.search_tv(tv_search_key).json()
            # print(tv_search_key, response)
            if response.get("results"):
                sync_status = utils.add_tv_show_to_db(tmdbapi.get_tv_show_by_id(
                    response["results"][0]["id"]),
                    details.get('location'),
                    details.get('media_dir_hash')
                )
                tvs[tv_show_name].update({
                    'tmdb_id': response["results"][0]["id"],
                    'name': response["results"][0]["name"],
                    'sync_status': sync_status
                })

        return Response({'movies': movies, 'tvs': tvs})


@api_view(['GET', 'PUT', 'DELETE'])
def handle_media_dirs(request, dir_type=None):
    if request.method == 'GET':
        print(settings.CONFIG.get())
        return Response(settings.CONFIG.get())

    # For updating the dir records
    if request.method == 'PUT':
        body = request.data
        if (not body.get('dir')) and (type(body.get('dir')) != str):
            return Response({'error': "Not a valid data, Please send a str in 'dir' key"}, 500)

        body['dir'] = body.get('dir').strip()

        if not Path(body.get('dir')).is_dir():
            return Response({'error': "Directory doesn't exists"}, 400)

        if (not dir_type) or dir_type.upper() == 'MOVIE':
            settings.CONFIG.add_to_movie_dirs(body.get('dir'))
        if (not dir_type) or dir_type.upper() == 'TV':
            settings.CONFIG.add_to_tv_dirs(body.get('dir'))
        settings.CONFIG.update()
        return Response(settings.CONFIG.get())

    if request.method == 'DELETE':
        body = request.data
        if (not body.get('dir')) and (type(body.get('dir')) != str):
            return Response({'error': "Not a valid data, Please send a str in 'dir' key"}, 500)

        body['dir'] = body.get('dir').strip()

        if (not dir_type) or dir_type.upper() == 'MOVIE':
            if body.get('dir') in settings.CONFIG.get().get('movie_dir'):
                settings.CONFIG.get().get('movie_dir').remove(body.get('dir'))

        if (not dir_type) or dir_type.upper() == 'TV':
            if body.get('dir') in settings.CONFIG.get().get('tv_dir'):
                settings.CONFIG.get().get('tv_dir').remove(body.get('dir'))

        settings.CONFIG.update()
        return Response(settings.CONFIG.get())
