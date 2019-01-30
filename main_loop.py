import logging
import signal
import sys
import time
import threading

from pirc522 import RFID

import async_button
import mpd_player
import music_copy
import rgb_led
import sound_effect
import usb
from config import LOGGER as LOG_CONF

run = True
rdr = RFID()
util = rdr.util()
util.debug = True

# Logger configuration
logging.basicConfig(level=logging.DEBUG,
                    format=LOG_CONF.LOG_FORMAT,
                    datefmt=LOG_CONF.LOG_DATE_FORMAT,
                    filename=LOG_CONF.LOG_FILE)

log = logging.getLogger(__name__)


def end_read(signal, frame):
    global run
    print("\nCtrl+C captured, ending read.")
    log.info("Ctrl+C captured, ending read.")
    run = False
    player.stop()
    button_stop_event.set()
    time.sleep(2)
    # rgb_led.ready_led_stop_pulse()
    rgb_led.off()
    rdr.cleanup()
    sys.exit()


signal.signal(signal.SIGINT, end_read)

player = mpd_player.Player()
player.stop()
playing_uid = ''
config_mode = False
config_started = False
rgb_led.setup()
rgb_led.ready_pause_led_on()
sound_effect.started()
log.info('************ START ************')


def play_list_on_tag():
    global playing_uid
    global config_mode
    global config_started
    # rdr.wait_for_tag()

    if config_started:
        return

    if usb.has_usb_stick():
        if not config_mode:
            sound_effect.start_config()
            log.info("config mode")
        config_mode = True
        player.stop()
        # rgb_led.ready_led_stop_pulse()
        rgb_led.config_led_on()
    else:
        if config_mode:
            log.info("player mode")
        config_mode = False
        # rgb_led.config_led_stop_blink()
        if player.is_playing():
            rgb_led.ready_led_on()
        else:
            rgb_led.ready_pause_led_on()

    (request_error, data) = rdr.request()
    if not request_error and data is not None:
        (anti_coll_error, uid) = rdr.anticoll()
        if not anti_coll_error:
            dash_uid = "-".join([str(i) for i in uid])
            if config_mode:
                config_started = True
                log.info('config started')
                # rgb_led.config_led_blink()
                rgb_led.copy_led_on()
                music_copy.copy_from_usb(dash_uid)
                sound_effect.end_config()
                # leave config mode when usb stick is removed
                while usb.has_usb_stick():
                    time.sleep(0.08)
                config_started = False
            if dash_uid == playing_uid:
                log.info(dash_uid + " is already selected")
                if not player.is_playing():
                    player.play()
            else:
                log.debug("UID: " + dash_uid)
                log.debug("Registered: " + str(music_copy.is_uid_registered(dash_uid)))

                if music_copy.is_uid_registered(dash_uid):
                    sound_effect.tag_scanned()
                    player.stop()
                    player.load_list(dash_uid)
                    player.play()
                    # rgb_led.ready_led_stop_pulse()
                    rgb_led.ready_led_on()
                    playing_uid = dash_uid


# start button check loop
log.info('Start async_button thread')
main_event = threading.Event()
button_stop_event = async_button.start(main_event)

log.info('start main loop')
while run and not main_event.is_set():
    play_list_on_tag()
    time.sleep(0.08)
