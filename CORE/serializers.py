from rest_framework import serializers
from .models import Media, Video, Genre


class MovieCollectionListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = (
            'name', 'tmdb_id', 'poster_image'
        )


class MovieCollectionPartsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Media
        fields = (
            'name', 'tmdb_id', 'poster_image',
        )


class SingleMovieCollectionSerializer(serializers.ModelSerializer):
    parts = serializers.SerializerMethodField()

    class Meta:
        model = Media
        fields = (
            'name', 'description', 'tmdb_id', 'background_image', 'poster_image', 'parts'
        )

    def get_parts(self, obj):
        parts = Video.objects.filter(list=obj)
        return MovieCollectionPartsSerializer(parts, many=True).data


class MovieDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = (
            'name', 'description', 'tmdb_id', 'background_image', 'logo', 'genre', 'location'
        )


class MovieListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = (
             'name', 'description', 'tmdb_id', 'poster_image', 'thumbnail', 'genre', 'popularity', 'timestamp', 'rating', 'release_date'
        )


class GenreListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = (
            'tmdb_id', 'name'
        )


class GenreMovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = (
            'name', 'description', 'tmdb_id', 'poster_image', 'thumbnail', 'genre'
        )


class GenreDetailsSerializer(serializers.ModelSerializer):
    movie_list = serializers.SerializerMethodField()

    class Meta:
        model = Genre
        fields = (
            'tmdb_id', 'name', 'movie_list'
        )

    @staticmethod
    def get_movie_list(obj):
        parts = Video.objects.filter(genre__icontains=obj.tmdb_id)
        return GenreMovieSerializer(parts, many=True).data
