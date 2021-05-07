from rest_framework import serializers
from .models import Media, Video, Genre, TVShow


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


class GenreListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = (
            'tmdb_id', 'name'
        )


# ------------------------- new -------------------------
class MovieListSerializer(serializers.ModelSerializer):
    genres = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = (
            'name', 'description', 'tmdb_id', 'poster_image', 'thumbnail', 'genres', 'popularity', 'rating',
            'release_date'
        )

    @staticmethod
    def get_genres(obj):
        genre_list = obj.genre.all()
        return GenreSerializer(genre_list, many=True).data


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = (
            'tmdb_id', 'name'
        )


class GenreMovieSerializer(serializers.ModelSerializer):
    genres = serializers.SerializerMethodField()

    class Meta:
        model = Video
        fields = (
            'name', 'description', 'tmdb_id', 'poster_image', 'thumbnail', 'genres', 'rating'
        )

    @staticmethod
    def get_genres(obj):
        genre_list = obj.genre.all()
        return GenreSerializer(genre_list, many=True).data


class GenreTVShowSerializer(serializers.ModelSerializer):
    genres = serializers.SerializerMethodField()

    class Meta:
        model = TVShow
        fields = (
            'name', 'description', 'tmdb_id', 'poster_image', 'thumbnail', 'genres', 'season_count', 'rating'
        )

    @staticmethod
    def get_genres(obj):
        genre_list = obj.genre.all()
        return GenreSerializer(genre_list, many=True).data


class GenreDetailsSerializer(serializers.ModelSerializer):
    movies = serializers.SerializerMethodField()
    tv_shows = serializers.SerializerMethodField()

    class Meta:
        model = Genre
        fields = (
            'tmdb_id', 'name', 'movies', 'tv_shows'
        )

    @staticmethod
    def get_movies(obj):
        movies_list = obj.video_set.filter(type='M').order_by('-popularity')
        return GenreMovieSerializer(movies_list, many=True).data

    @staticmethod
    def get_tv_shows(obj):
        tv_show_list = obj.tvshow_set.all().order_by('-popularity')
        return GenreTVShowSerializer(tv_show_list, many=True).data
