from django.db import models
import json


# Create your models here.
class Genre(models.Model):
    tmdb_id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=100, null=False, blank=False)

    def get_movies(self):
        return Video.objects.filter(genre__icontains=self.tmdb_id)

    def __str__(self):
        return '{}'.format(self.tmdb_id)


class Media(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField()
    type = models.CharField(max_length=5)
    tmdb_id = models.IntegerField()

    background_image = models.CharField(max_length=100, blank=True, null=True)
    poster_image = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return '{} [{}]'.format(self.name, self.tmdb_id)


class Video(models.Model):
    collection = models.ForeignKey(Media, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField()
    location = models.CharField(max_length=100)
    genre = models.CharField(max_length=200, null=True, blank=True)
    type = models.CharField(max_length=5)
    tmdb_id = models.IntegerField()

    logo = models.CharField(max_length=100, blank=True, null=True)
    thumbnail = models.CharField(max_length=100, blank=True, null=True)
    background_image = models.CharField(max_length=100, blank=True, null=True)
    poster_image = models.CharField(max_length=100, blank=True, null=True)

    rating = models.FloatField(null=True, blank=True)
    popularity = models.FloatField(null=True, blank=True)
    release_date = models.DateField(null=True, blank=True)
    timestamp = models.DateTimeField(null=True, blank=True)

    def get_genre(self):
        genre_dict = {}
        if not self.genre:
            return genre_dict
        for genre_id in json.loads(self.genre):
            try:
                genre = Genre.objects.get(tmdb_id=genre_id)
                genre_dict[genre.tmdb_id] = genre.name
            except Genre.DoesNotExist:
                pass
        return genre_dict

    def get_genre_ids(self):
        return list(self.get_genre().keys())

    def set_genre(self, genre_list):
        if type(genre_list) is not list:
            raise Exception('Genre must be a list')
        # for genre_id in genre_list:
        #     if genre = Genre.objects.get(tmdb_id=genre_id)

        self.genre = json.loads(self.genre)
        return self.get_genre()

    def add_genre(self, genre_id):
        genre_list = self.get_genre()
        genre_obj = Genre.objects.get(tmdb_id=genre_id)
        print(genre_list, genre_obj.tmdb_id)
        genre_list.append(genre_obj.tmdb_id)
        print(genre_list)
        return self.get_genre_object()

    def __str__(self):
        return '{} [{}]'.format(self.name, self.tmdb_id)
