from pathlib import Path


def get_media_dirs(media_dir_stream):
    # movie_dir = list(map(lambda x: Path(x), ))
    # tv_dir = list(map(lambda x: Path(x), media_dir_stream[1].replace('\n', '').replace('\r', '').split(',')))
    result = dict()
    movie_dir_map = dict()
    for media_location in media_dir_stream[0].replace('\n', '').replace('\r', '').split(','):
        movie_dir_map[hash(media_location)] = Path(media_location)

    tv_dir_map = dict()
    for tv_location in media_dir_stream[1].replace('\n', '').replace('\r', '').split(','):
        tv_dir_map[hash(tv_location)] = Path(tv_location)

    result['movie_dir_map'] = movie_dir_map
    result['tv_dir_map'] = tv_dir_map
    result['movie_dirs'] = list(movie_dir_map.values())
    result['tv_dirs'] = list(tv_dir_map.values())

    return result
