from rest_framework import serializers

from CORE.models import Video

from .models import Watchlist, UserProfile


class MovieListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = (
            'name', 'description', 'tmdb_id', 'poster_image', 'thumbnail', 'genre', 'popularity', 'timestamp', 'rating',
            'release_date'
        )


class GenreDetailsSerializer(serializers.ModelSerializer):
    movie_list = serializers.SerializerMethodField()

    class Meta:
        model = Watchlist
        fields = (
            'user', 'video', 'duration'
        )

    @staticmethod
    def get_movie_list(obj):
        parts = Video.objects.filter(genre__icontains=obj.tmdb_id).order_by('-popularity')
        return MovieListSerializer(parts, many=True).data


class WishlistSerializer(serializers.ModelSerializer):
    # Wishlist = serializers.RelatedField()

    class Meta:
        model = Video
        fields = (
            'name', 'description', 'genre', 'type', 'poster_image', 'thumbnail'
        )

    @staticmethod
    def get_movie_list(obj):
        parts = Video.objects.filter(genre__icontains=obj.tmdb_id).order_by('-popularity')
        return MovieListSerializer(parts, many=True).data
