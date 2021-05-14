import os
import re
from rest_framework.response import Response
from rest_framework.views import APIView
from . import utils


# Create your views here.
class Sync(APIView):
    def get(self, request, format=None):
        tmdbapi = utils.TMDBAPI()
        movies = utils.get_all_static_file_stat()
        for movie_name, details in movies.items():
            search_key = re.compile('[\w ]*').match(movie_name).group()
            response = tmdbapi.search(search_key).json()
            if response["results"]:
                print(response['results'][0])
                movies[movie_name].append(response["results"][0]["id"])
                movies[movie_name].append(response["results"][0]["original_title"])
                sync_status = utils.add_movie_to_db(tmdbapi.get_movie_by_id(response["results"][0]["id"]), movie_name)
                movies[movie_name].append({'sync_status': sync_status})

        return Response(movies)
