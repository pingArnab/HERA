import os
import re
from rest_framework.response import Response
from rest_framework.views import APIView
from . import utils


# Create your views here.
class Sync(APIView):
    def get(self, request, format=None):
        tmdbapi = utils.TMDBAPI()
        movies = utils.get_all_movie_file_stat()
        for movie_name, details in movies.items():
            movie_search_key = re.compile('[\w ]*').match(movie_name).group()
            response = tmdbapi.search_movie(movie_search_key).json()
            if response["results"]:
                movies[movie_name].append(response["results"][0]["id"])
                movies[movie_name].append(response["results"][0]["original_title"])
                sync_status = utils.add_movie_to_db(tmdbapi.get_movie_by_id(response["results"][0]["id"]), movie_name)
                movies[movie_name].append({'sync_status': sync_status})

        tvs = utils.get_all_tv_show_file_stat()
        for tv_show_name, details in tvs.items():
            tv_search_key = re.compile('[\w ]*').match(tv_show_name).group()
            response = tmdbapi.search_tv(tv_search_key).json()
            # print(tv_search_key, response)
            if response["results"]:
                sync_status = utils.add_tv_show_to_db(tmdbapi.get_tv_show_by_id(
                    response["results"][0]["id"]),
                    details.get('location')
                )
                tvs[tv_show_name].update({
                    'tmdb_id': response["results"][0]["id"],
                    'name': response["results"][0]["name"],
                    'sync_status': sync_status
                })

        return Response({'movies': movies, 'tvs': tvs})
