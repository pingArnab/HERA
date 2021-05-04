from rest_framework import serializers
from .models import Media, Video


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
