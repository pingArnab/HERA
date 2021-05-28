import json

from django.shortcuts import render
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import api_view

import CORE.models
from .serializers import MovieListSerializer, WishlistSerializer
from .models import UserProfile
from CORE.models import Video, TVShow


# Create your views here.
@permission_classes([IsAuthenticated])
class Recommendation(APIView):
    def get(self, request, format=None):
        movies = request.user.AuthUser.watchlist_set

        # print(type(request.user))
        # print(request.user.AuthUser)
        # print(User.objects.get(dj_user=request.user))
        #
        # search_filters = []
        # for key in q_list:
        #     search_filters.append(Q(name__icontains=key))
        #     search_filters.append(Q(description__icontains=key))
        #     search_filters.append(Q(genre__icontains=key))
        #
        # video = Video.objects.filter(type='M').filter(reduce(operator.or_, search_filters)).order_by('-popularity')
        serializer = MovieListSerializer(movies, many=True)
        return Response(serializer.data)

        # return JsonResponse({'qq': })


@permission_classes([IsAuthenticated])
@api_view(['GET', 'POST', 'DELETE'])
def wishlist(request):
    userProfile, status = UserProfile.objects.get_or_create(dj_user=request.user)
    if status:
        userProfile.save()
    if request.method == 'GET':
        tv_list = userProfile.tv_wishlist.all()
        tv_list_serializer = WishlistSerializer(tv_list, many=True)
        movie_list = userProfile.movie_wishlist.filter(type=CORE.models.MediaType.MOVIE)
        movie_list_serializer = WishlistSerializer(movie_list, many=True)
        return Response({
            'movies': movie_list_serializer.data,
            'tvs': tv_list_serializer.data,
        })
    if request.method == 'POST':
        tmdb_id = json.loads(request.body).get('tmdb_id')
        if not tmdb_id:
            return Response({'error': 'Please send TMDB id'}, status=400)

        if Video.objects.filter(tmdb_id=tmdb_id):
            video = Video.objects.get(tmdb_id=tmdb_id)
            userProfile.movie_wishlist.add(video)
        elif TVShow.objects.filter(tmdb_id=tmdb_id):
            tv = TVShow.objects.get(tmdb_id=tmdb_id)
            userProfile.movie_wishlist.add(tv)
        else:
            return Response({'error': 'invalid TMDB id in adding wishlist'})

    if request.method == 'DELETE':
        tmdb_id = json.loads(request.body).get('tmdb_id')
        if not tmdb_id:
            return Response({'error': 'Please send TMDB id'}, status=400)

        if Video.objects.filter(tmdb_id=tmdb_id):
            video = Video.objects.get(tmdb_id=tmdb_id)
            userProfile.movie_wishlist.remove(video)
        elif TVShow.objects.filter(tmdb_id=tmdb_id):
            tv = TVShow.objects.get(tmdb_id=tmdb_id)
            userProfile.movie_wishlist.remove(tv)
        else:
            return Response({'error': 'invalid TMDB id in remove wishlist'})

    userProfile.save()
    return Response({'status': True})
