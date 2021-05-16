import datetime
import os
import pathlib
import traceback

import requests
from django.conf import settings

from CORE.models import Media, Video, Genre, TVShow

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
        traceback.print_exc()
    return file_date


def get_all_movie_file_stat():
    stat = dict()
    for directory in settings.MOVIES_DIRS:
        stat.update(get_dir_files_stat(directory))
    return stat


def get_dir_tv_shows_stat(directory=None):
    file_date = dict()
    try:
        directory and os.chdir(directory)
        for file in [name for name in os.listdir() if os.path.isdir(os.path.join(name))]:
            create_time = datetime.datetime.fromtimestamp(pathlib.Path(file).stat().st_mtime)
            is_sync = create_time < last_sync
            file_date[file] = [create_time, is_sync]
    except Exception as e:
        print(e)
        traceback.print_exc()
    print(file_date)
    return file_date


def get_all_tv_show_file_stat():
    stat = dict()
    for directory in settings.TVSHOWS_DIRS:
        print(directory)
        stat.update(get_dir_tv_shows_stat(directory))
    return stat


def get_genre_array(genre_ids=None):
    tmdbapi = TMDBAPI()
    if genre_ids:
        genres = []
        for linked_genre in genre_ids:
            genre_id = linked_genre['id']
            if Genre.objects.filter(tmdb_id=genre_id):
                genres.append(Genre.objects.get(tmdb_id=genre_id))
            else:
                try:
                    all_genres = tmdbapi.get_all_genre()
                    if all_genres.get(genre_id):
                        genre = Genre.objects.create(
                            tmdb_id=genre_id,
                            name=all_genres[genre_id]
                        )
                        genre.save()
                        genres.append(genre)
                except Exception as e:
                    print(e)
                    traceback.print_exc()
        return genres


def add_tv_show_to_db(tmdb_data):
    if TVShow.objects.filter(tmdb_id=tmdb_data['id']):
        return True

    tmdbapi = TMDBAPI()
    fanartapi = FanartAPI()
    tv_shows = None
    try:
        tv_shows = TVShow.objects.create(
            tmdb_id=tmdb_data.get('id'),
            name=tmdb_data.get('name'),
            description=tmdb_data.get('overview'),
            type='T',

            rating=tmdb_data.get('vote_average'),
            popularity=tmdb_data.get('popularity'),
            tagline=tmdb_data.get('tagline'),
        )

        if tmdb_data.get('poster_path'):
            tv_shows.poster_image = TMDBAPI.TMDB_IMAGE_URL + tmdb_data.get('poster_path')
        if tmdb_data.get('backdrop_path'):
            tv_shows.background_image = TMDBAPI.TMDB_IMAGE_URL + tmdb_data.get('backdrop_path')
        if tmdb_data['genres']:
            tv_shows.genre.add(*get_genre_array(tmdb_data['genres']))

        if tmdb_data['seasons']:
            tv_shows.season_count = len(tmdb_data['seasons'])
            tv_shows.release_date = datetime.datetime.strptime(tmdb_data['seasons'][0]['air_date'], '%Y-%m-%d').date()

        logo_and_thumbnail = fanartapi.get_logo_and_thumbnail(tmdb_data.get('id'), 'tv')
        if logo_and_thumbnail:
            tv_shows.logo = logo_and_thumbnail.get('logo')
            tv_shows.thumbnail = logo_and_thumbnail.get('thumbnail')

        trailer = tmdbapi.get_trailer(tmdb_data.get('id'), 'tv')
        if trailer:
            tv_shows.trailer = trailer

        if tmdb_data.get('episode_run_time'):
            tv_shows.episode_runtime = datetime.timedelta(
                minutes=int(tmdb_data.get('episode_run_time')[0])
            ) if type(tmdb_data.get('episode_run_time')[0]) is int else None

        tv_shows.save()
        return True
    except Exception as e:
        if tv_shows:
            tv_shows.delete()
        print('Ex--------------', e)
        traceback.print_exc()
        return False


def add_movie_to_db(tmdb_data, filename):
    if Video.objects.filter(tmdb_id=tmdb_data['id']):
        video = Video.objects.get(tmdb_id=tmdb_data['id'])
        video.location = '/static/' + filename
        return True
    video = None
    media = None
    tmdbapi = TMDBAPI()
    fanartapi = FanartAPI()
    try:
        video = Video.objects.create(
            tmdb_id=tmdb_data.get('id'),
            name=tmdb_data.get('original_title'),
            description=tmdb_data.get('overview'),
            location='/static/' + filename,
            type='M',
            rating=tmdb_data.get('vote_average'),
            added_at=datetime.datetime.now(),
            popularity=tmdb_data.get('popularity'),
            tagline=tmdb_data.get('tagline'),
        )
        if tmdb_data.get('poster_path'):
            video.poster_image = TMDBAPI.TMDB_IMAGE_URL + tmdb_data.get('poster_path')
        if tmdb_data.get('backdrop_path'):
            video.background_image = TMDBAPI.TMDB_IMAGE_URL + tmdb_data.get('backdrop_path')

        video.duration = datetime.timedelta(minutes=int(tmdb_data.get('runtime'))) if type(
            tmdb_data.get('runtime')) is int else None

        logo_and_thumbnail = fanartapi.get_logo_and_thumbnail(tmdb_data.get('id'), 'movie')
        if logo_and_thumbnail:
            video.logo = logo_and_thumbnail.get('logo')
            video.thumbnail = logo_and_thumbnail.get('thumbnail')

        trailer = tmdbapi.get_trailer(tmdb_data.get('id'), 'movie')
        if trailer:
            video.trailer = trailer

        try:
            video.release_date = datetime.datetime.strptime(tmdb_data.get('release_date'), '%Y-%m-%d').date()
        except Exception as ex:
            print(ex)
            traceback.print_exc()

        if tmdb_data['genres']:
            video.genre.add(*get_genre_array(tmdb_data['genres']))

        if tmdb_data['belongs_to_collection']:
            if Media.objects.filter(tmdb_id=tmdb_data['belongs_to_collection']['id']):
                media = Media.objects.get(tmdb_id=tmdb_data['belongs_to_collection']['id'])
            else:
                collection = tmdbapi.get_collection_by_id(tmdb_data['belongs_to_collection']['id'])

                media = Media.objects.create(
                    tmdb_id=collection.get('id'),
                    name=collection.get('name').replace('Collection', '').strip(),
                    description=collection.get('overview'),
                    type='M',
                    is_collection=True,
                    background_image=TMDBAPI.TMDB_IMAGE_URL + collection.get('backdrop_path'),
                    poster_image=TMDBAPI.TMDB_IMAGE_URL + collection.get('poster_path')
                )
            media.save()
            # print('----------------------', media)
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

    def search_movie(self, search_key=None):
        # print('---------', search_key)
        search_url = self.TMDB_URL + '/search/movie' + self.TMDB_EXTRAS \
                     + "&query={search_key}&page=1&include_adult=false".format(search_key=search_key)
        response = requests.get(search_url)
        return response

    def search_tv(self, search_key=None):
        # print('---------', search_key)
        search_url = self.TMDB_URL + '/search/tv' + self.TMDB_EXTRAS \
                     + "&query={search_key}&page=1&include_adult=false".format(search_key=search_key)
        response = requests.get(search_url)
        return response

    def get_movie_by_id(self, movie_id):
        movie_url = self.TMDB_URL + '/movie/{movie_id}'.format(movie_id=movie_id) + self.TMDB_EXTRAS
        response = requests.get(movie_url)
        return response.json()

    def get_tv_show_by_id(self, movie_id):
        tv_url = self.TMDB_URL + '/tv/{movie_id}'.format(movie_id=movie_id) + self.TMDB_EXTRAS
        response = requests.get(tv_url)
        return response.json()

    def get_collection_by_id(self, collection_id):
        collection_url = self.TMDB_URL + '/collection/{collection_id}'.format(
            collection_id=collection_id) + self.TMDB_EXTRAS
        # print(collection_id, type(collection_id), ' | ', collection_url)
        response = requests.get(collection_url)
        return response.json()

    def get_all_genre(self):
        genre_url = self.TMDB_URL + '/genre/movie/list' + self.TMDB_EXTRAS
        # print(genre_url)
        response = requests.get(genre_url)
        genres = dict()
        for genre in response.json().get('genres'):
            genres[genre['id']] = genre['name']
        return genres

    def get_trailer(self, tmdb_id, media_type=None):

        trailer_url = self.TMDB_URL + '/{media_type}/{tmdb_id}/videos'.format(
            media_type=media_type.lower(),
            tmdb_id=tmdb_id
        ) + self.TMDB_EXTRAS
        # print(trailer_url)
        response = requests.get(trailer_url)
        data = response.json()['results']
        trailer = None
        for video in data:
            if video.get('type') == "Trailer":
                return 'https://www.youtube.com/watch?v=' + video.get('key')
        return None

    # https://api.themoviedb.org/3/tv/71912/external_ids?api_key=adfff9c3b0688cc13ae8d7b0291b257e&language=en-US
    def get_external_ids(self, tmdb_id, media_type=None):
        external_ids_url = self.TMDB_URL + '/{media_type}/{tmdb_id}/external_ids'.format(
            media_type=media_type.lower(),
            tmdb_id=tmdb_id
        ) + self.TMDB_EXTRAS
        return requests.get(external_ids_url).json()

# https://webservice.fanart.tv/v3/movies/673?api_key=0a07e4f6e89f662683254b31e370bedb
class FanartAPI:
    FANART_API_KEY = '0a07e4f6e89f662683254b31e370bedb'
    FANART_URL = 'https://webservice.fanart.tv/v3'
    FANART_EXTRAS = '?api_key={api_key}'.format(api_key=FANART_API_KEY)

    def get_logo_and_thumbnail(self, tmdb_id, media_type=None):
        res = dict()
        media_id = None
        if media_type.lower() == 'movie':
            media_id = tmdb_id
            media_type = media_type.lower()
        elif media_type.lower() == 'tv':
            tmdbapi = TMDBAPI()
            external_ids = tmdbapi.get_external_ids(tmdb_id=tmdb_id, media_type=media_type)
            media_id = external_ids.get('tvdb_id')
            media_type = media_type.lower()
        logo_and_thumbnail_url = self.FANART_URL + '/{media_type}/{id}'.format(
            media_type=media_type,
            id=media_id
        ) + self.FANART_EXTRAS
        response = requests.get(logo_and_thumbnail_url)
        data = response.json()
        # print("line: 183", data)
        if data.get('{media_type}logo'.format(media_type=media_type)):
            for logo in data['{media_type}logo'.format(media_type=media_type)]:
                if logo['lang'] == 'en':
                    res['logo'] = logo['url']
                    break
            if not res['logo']:
                res['logo'] = data['{media_type}logo'.format(media_type=media_type)][0]['url']
        elif data.get('hd{media_type}logo'.format(media_type=media_type)):
            for logo in data['hd{media_type}logo'.format(media_type=media_type)]:
                if logo['lang'] == 'en':
                    res['logo'] = logo['url']
                    break
            if not res['logo']:
                res['logo'] = data['hd{media_type}logo'.format(media_type=media_type)][0]['url']
        else:
            res['logo'] = None

        if data.get('{media_type}thumb'.format(media_type=media_type)):
            for logo in data['{media_type}thumb'.format(media_type=media_type)]:
                if logo['lang'] == 'en':
                    res['thumbnail'] = logo['url']
                    break
            if not res['logo']:
                res['thumbnail'] = data['{media_type}thumb'.format(media_type=media_type)][0]['url']
        else:
            res['thumbnail'] = None

        return res
