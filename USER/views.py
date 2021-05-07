from django.shortcuts import render
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import JsonResponse

from .serializers import MovieListSerializer, WishlistSerializer
from .models import UserProfile


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
class Wishlist(APIView):
    def get(self, request, format=None):
        movies = request.user.UserProfile.wishlist.all()

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
        serializer = WishlistSerializer(movies, many=True)
        return Response(serializer.data)

