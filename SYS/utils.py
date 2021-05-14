import os, glob
import pathlib
import datetime
from django.conf import settings

last_sync = datetime.datetime(2021, 5, 12)


def get_dir_files_stat(directory = None):
    file_date = dict()
    try:
        os.chdir(directory)
        for file in os.listdir():
            if file and (file in glob.glob('*.txt')):
                print(file, ' | ', type(file), '| line 13')
                create_time = datetime.datetime.fromtimestamp(pathlib.Path(file).stat().st_mtime)
                is_sync = create_time < last_sync
                file_date[file] = [create_time, is_sync]
    except Exception as e:
        print(e)
    return file_date


def get_all_static_file_stat():
    stat = dict()
    for directory in settings.STATICFILES_DIRS:
        print(directory, '\n-------------------------')
        # print(get_dir_files_stat(directory))
        stat.update(get_dir_files_stat(directory))
    return stat
