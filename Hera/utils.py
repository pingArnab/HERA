from pathlib import Path
import hashlib

def get_media_dirs(media_dir_stream):
    result = dict()
    movie_dir_map = dict()
    for media_location in media_dir_stream[0].replace('\n', '').replace('\r', '').split(','):
        movie_dir_map[hashlib.md5(media_location.encode('utf-8')).hexdigest()] = Path(media_location)

    tv_dir_map = dict()
    for tv_location in media_dir_stream[1].replace('\n', '').replace('\r', '').split(','):
        tv_dir_map[hashlib.md5(tv_location.encode('utf-8')).hexdigest()] = Path(tv_location)

    result['movie_dir_map'] = movie_dir_map
    result['tv_dir_map'] = tv_dir_map
    result['movie_dirs'] = list(movie_dir_map.values())
    result['tv_dirs'] = list(tv_dir_map.values())

    return result
