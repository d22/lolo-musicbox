import os
import subprocess

from config import SOUNDEFFECTS


def started():
    play_effect(SOUNDEFFECTS.PRING_UP)


def tag_scanned():
    play_effect(SOUNDEFFECTS.PLING)


def song_copied():
    play_effect(SOUNDEFFECTS.CLIC)


def no_songs_to_copy():
    play_effect(SOUNDEFFECTS.ZURR)


def start_config():
    play_effect(SOUNDEFFECTS.PRING_UP)


def end_config():
    play_effect(SOUNDEFFECTS.PRING_DOWN)


def shutdown():
    play_effect(SOUNDEFFECTS.PRING_DOWN)


def play_effect(effect_name):
    command = 'mpg123'
    file = os.path.join(SOUNDEFFECTS.DIR, effect_name)
    devnull = open(os.devnull, 'w')
    subprocess.call([command, file], stdout=devnull, stderr=devnull)
