from django.db import models


# Create your models here.
class Media(models.Model):
    name = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField()
    type = models.CharField(max_length=5)
    tmdb_id = models.CharField(max_length=10)

    background_image = models.CharField(max_length=100, blank=True, null=True)
    poster_image = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return '{} [{}]'.format(self.name, self.tmdb_id)


class Video(models.Model):
    list = models.ForeignKey(Media, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, null=False, blank=False)
    description = models.TextField()
    location = models.CharField(max_length=100)
    genre = models.CharField(max_length=200, null=True, blank=True)
    type = models.CharField(max_length=5)
    tmdb_id = models.CharField(max_length=10)

    logo = models.CharField(max_length=100, blank=True, null=True)
    thumbnail = models.CharField(max_length=100, blank=True, null=True)
    background_image = models.CharField(max_length=100, blank=True, null=True)
    poster_image = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return '{} [{}]'.format(self.name, self.tmdb_id)


