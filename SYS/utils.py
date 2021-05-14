import os, glob
import pathlib
import datetime
import traceback
import requests
from django.conf import settings
from CORE.models import Media, Video, Genre

last_sync = datetime.datetime(2021, 5, 12)


def get_dir_files_stat(directory=None):
    file_date = dict()
    try:
        os.chdir(directory)
        for file in os.listdir():
            if file and (os.path.splitext(file)[1] in ['.mp4', '.mpeg4', '.webm', '.mkv', '.wmv', '.avi']):
                create_time = datetime.datetime.fromtimestamp(pathlib.Path(file).stat().st_mtime)
                is_sync = create_time < last_sync
                file_date[file] = [create_time, is_sync]
    except Exception as e:
        print(e)
    return file_date


def get_all_static_file_stat():
    stat = dict()
    for directory in settings.STATICFILES_DIRS:
        stat.update(get_dir_files_stat(directory))
    return stat


def add_movie_to_db(tmdb_data, filename):
    print('=======', tmdb_data, filename)
    if Video.objects.filter(tmdb_id=tmdb_data['id']):
        video = Video.objects.get(tmdb_id=tmdb_data['id'])
        video.location = '/static/' + filename
        return True
    video = None
    media = None
    tmdbapi = TMDBAPI()
    try:
        video = Video.objects.create(
            tmdb_id=tmdb_data.get('id'),
            name=tmdb_data.get('original_title'),
            description=tmdb_data.get('overview'),
            location='/static/' + filename,
            type='M',
            thumbnail=TMDBAPI.TMDB_IMAGE_URL + tmdb_data.get('backdrop_path'),
            rating=tmdb_data.get('vote_average'),
            added_at=datetime.datetime.now(),
            poster_image=TMDBAPI.TMDB_IMAGE_URL + tmdb_data.get('poster_path'),
            background_image=TMDBAPI.TMDB_IMAGE_URL + tmdb_data.get('backdrop_path'),
            popularity=tmdb_data.get('popularity'),
            tagline=tmdb_data.get('tagline'),
        )
        video.duration = datetime.timedelta(minutes=int(tmdb_data.get('runtime')) * 60) if type(tmdb_data.get('runtime')) is int else None
        if tmdb_data['genres']:
            genres = []
            for linked_genre in tmdb_data['genres']:
                genre_id = linked_genre['id']
                if Genre.objects.filter(tmdb_id=genre_id):
                    genres.append(Genre.objects.get(tmdb_id=genre_id))
                else:
                    try:
                        all_genres = tmdbapi.get_all_genre()
                        genre = Genre.objects.create(
                            tmdb_id=genre_id,
                            name=all_genres[genre_id]
                        )
                        genre.save()
                        genres.append(genre)
                    except Exception as e:
                        print(e)
            video.genre.add(*genres)

        video.genre.add()
        print('----------------------', video)
        if tmdb_data['belongs_to_collection']:
            if Media.objects.filter(tmdb_id=tmdb_data['belongs_to_collection']['id']):
                media = Media.objects.get(tmdb_id=tmdb_data['belongs_to_collection']['id'])
            else:
                collection = tmdbapi.get_collection_by_id(tmdb_data['belongs_to_collection']['id'])

                media = Media.objects.create(
                    tmdb_id=collection.get('id'),
                    name=collection.get('name'),
                    description=collection.get('overview'),
                    type='M',
                    is_collection=True,
                    background_image=TMDBAPI.TMDB_IMAGE_URL + collection.get('backdrop_path'),
                    poster_image=TMDBAPI.TMDB_IMAGE_URL + collection.get('poster_path')
                )
            media.save()
            print('----------------------', media)
            video.media = media

        video.save()
        return True
    except Exception as e:
        if video:
            video.delete()
        if media and not media.video_set.all():
            media.delete()
        print('Ex--------------', e)
        traceback.print_exc()
        return False


class TMDBAPI:
    TMDB_API_KEY = 'adfff9c3b0688cc13ae8d7b0291b257e'
    TMDB_URL = 'https://api.themoviedb.org/3'
    TMDB_IMAGE_URL = 'https://image.tmdb.org/t/p/original'
    TMDB_EXTRAS = '?api_key={api_key}&language=en-US'.format(api_key=TMDB_API_KEY)

    def search(self, search_key=None):
        # print('---------', search_key)
        search_url = self.TMDB_URL + '/search/movie' + self.TMDB_EXTRAS \
                     + "&query={search_key}&page=1&include_adult=false".format(search_key=search_key)
        response = requests.get(search_url)
        return response

    def get_movie_by_id(self, movie_id):
        movie_url = self.TMDB_URL + '/movie/{movie_id}'.format(movie_id=movie_id) + self.TMDB_EXTRAS
        print(movie_id, type(movie_id), ' | ', movie_url)
        response = requests.get(movie_url)
        return response.json()

    def get_collection_by_id(self, collection_id):
        collection_url = self.TMDB_URL + '/collection/{collection_id}'.format(
            collection_id=collection_id) + self.TMDB_EXTRAS
        print(collection_id, type(collection_id), ' | ', collection_url)
        response = requests.get(collection_url)
        return response.json()

    def get_all_genre(self):
        genre_url = self.TMDB_URL + '/genre/movie/list' + self.TMDB_EXTRAS
        print(genre_url)
        response = requests.get(genre_url)
        genres = dict()
        for genre in response.json().get('genres'):
            genres[genre['id']] = genre['name']
        return genres
