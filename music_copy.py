import glob
import logging
import os
import random
import shutil
import sys

import mpd_player
import usb
import sound_effect
from config import PATHS as CONF

log = logging.getLogger(__name__)


def copy_from_usb(target_dir_name):
    try:
        if not usb.has_usb_stick():
            log.info('no usb stick present, skipping')
            return
        usb.auto_mount()
        source_dir = os.path.join(CONF.MOUNT_DIR, CONF.MUSIC_SRC_DIR)
        log.info('source dir: ' + source_dir)
        target_dir = CONF.MUSIC_DIR + target_dir_name + '/'
        log.info('target dir: ' + target_dir)
        temp_dir = get_temp_dir_name()
        log.info('temp-dir: ' + temp_dir)
        os.mkdir(temp_dir)

        log.info('start copying songs')
        for mp3 in glob.iglob(source_dir + '/**/*.mp3', recursive=True):
            log.info("copying " + mp3)
            target_file = temp_dir + os.path.basename(mp3)
            shutil.copyfile(mp3, target_file)
            sound_effect.song_copied()
            log.info('done')

        log.info('done copying songs')

        # no files where copied remove temp dir and do nothing
        if not os.listdir(temp_dir):
            sound_effect.no_songs_to_copy()
            log.warning('there were no songs to copy, dir name must be ' + CONF.MUSIC_SRC_DIR)
            os.removedirs(temp_dir)
            return

        # if target dir already exists, remove
        if os.path.exists(target_dir) is True:
            log.warning('target directory already exists, deleting (' + target_dir + ')')
            shutil.rmtree(target_dir)

        # rename temp dir to target dir
        os.rename(temp_dir, target_dir)
        # update mpd database
        log.info('update mpd database')
        mpd_player.Player.update()
    finally:
        usb.umount()


def get_temp_dir_name():
    rand_suffix = random.randint(1000, 9999)
    return CONF.MUSIC_DIR + "tmp-" + str(rand_suffix) + "/"


def is_uid_registered(uid):
    path = CONF.MUSIC_DIR + uid
    if os.path.exists(path):
        return True
    return False


def main(argv):
    copy_from_usb(argv[1])


if __name__ == "__main__":
    main(sys.argv)
