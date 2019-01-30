import logging
import subprocess
import threading
import time

import RPi.GPIO as GPIO

import mpd_player
import rgb_led
import sound_effect
from config import BUTTON as CONFIG

log = logging.getLogger(__name__)

# use board, since NFC/RFID Sensor library uses board
GPIO.setmode(GPIO.BOARD)
# next button
GPIO.setup(CONFIG.NEXT_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# prev button
GPIO.setup(CONFIG.PREV_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# pause button
GPIO.setup(CONFIG.PAUSE_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
# power button
GPIO.setup(CONFIG.POWER_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)

button_timeout = CONFIG.TIMEOUT
power_time = CONFIG.POWER_PRESS_TIME
power_counter = 0

player = mpd_player.Player()

g_main_event = None


def button_check_loop(arg1, event, main_event):
    global g_main_event
    g_main_event = main_event
    next_pushed = False
    prev_pushed = False
    pause_pushed = False
    power_pushed = False

    while not event.is_set():
        next_pushed = handle_next(next_pushed)
        prev_pushed = handle_prev(prev_pushed)
        pause_pushed = handle_pause(pause_pushed)
        power_pushed = handle_power(power_pushed)


def handle_next(next_pushed):
    state_next_button = GPIO.input(CONFIG.NEXT_PIN)
    if not state_next_button:
        if not next_pushed:
            log.debug('next-button pushed')
            next_pushed = True
            player.next()
            time.sleep(button_timeout)
    else:
        next_pushed = False
    return next_pushed


def handle_prev(prev_pushed):
    state_prev_button = GPIO.input(CONFIG.PREV_PIN)
    if not state_prev_button:
        if not prev_pushed:
            log.debug('prev-button pushed')
            prev_pushed = True
            player.prev()
            time.sleep(button_timeout)
    else:
        prev_pushed = False
    return prev_pushed


def handle_pause(pause_pushed):
    state_pause_button = GPIO.input(CONFIG.PAUSE_PIN)
    if not state_pause_button:
        if not pause_pushed:
            log.debug('pause-button pushed')
            pause_pushed = True
            player.toggle()
            if player.is_playing():
                # rgb_led.ready_led_stop_pulse()
                rgb_led.ready_led_on()
            else:
                # rgb_led.ready_led_pulse()
                rgb_led.ready_pause_led_on()
            time.sleep(button_timeout)
    else:
        pause_pushed = False
    return pause_pushed


def handle_power(power_pushed):
    global power_counter
    state_pause_button = GPIO.input(CONFIG.POWER_PIN)
    if not state_pause_button:
        if not power_pushed:
            log.debug('power-button pushed')
            power_pushed = True

        if power_pushed:
            time.sleep(button_timeout)
            power_counter += button_timeout
            log.debug("counter:" + str(power_counter))
            if power_counter >= CONFIG.POWER_PRESS_TIME:
                log.debug("Shutting down the system")
                if g_main_event is not None:
                    g_main_event.set()
                time.sleep(0.5)
                rgb_led.power_off_led_on()
                player.stop()
                sound_effect.shutdown()
                time.sleep(1)
                subprocess.call(['sudo', 'shutdown', '-h', 'now'], shell=False)

    else:
        power_pushed = False
        power_counter = 0
    return power_pushed


def start(main_event=None):
    button_stop_event = threading.Event()
    button_thread = threading.Thread(target=button_check_loop, args=(1, button_stop_event, main_event))
    button_thread.start()
    return button_stop_event
