import logging
import threading
import time

import RPi.GPIO as GPIO

from config import LED

log = logging.getLogger(__name__)

red_pin = LED.RED_PIN
green_pin = LED.GREEN_PIN
blue_pin = LED.BLUE_PIN

ready_pulse_event = None
conf_blink_event = None


def ready_led_on():
    off()
    green()


def ready_pause_led_on():
    off()
    magenta()


def config_led_on():
    off()
    blue()


def copy_led_on():
    off()
    cyan()


def power_off_led_on():
    off()
    red()


def config_led_blink():
    global conf_blink_event
    conf_blink_event = threading.Event()
    blinker = threading.Thread(target=blink, args=(blue, conf_blink_event))
    blinker.start()


def config_led_stop_blink():
    global conf_blink_event
    if conf_blink_event is not None:
        conf_blink_event.set()
        off()
        time.sleep(2 * LED.BLINK_SLEEP)


def blink(color_func, e):
    log.debug('start blink')
    while not e.is_set():
        color_func()
        time.sleep(LED.BLINK_SLEEP)
        off()
        time.sleep(LED.BLINK_SLEEP)

    log.debug('end blink')


def ready_led_pulse():
    global ready_pulse_event
    ready_pulse_event = threading.Event()
    pulsing = threading.Thread(target=pulse, args=(green_pin, ready_pulse_event))
    pulsing.start()


def ready_led_stop_pulse():
    global ready_pulse_event
    if ready_pulse_event is not None:
        ready_pulse_event.set()
        ready_led_on()


def pulse(channel, e):
    frequency = 300
    speed = 0.08
    step = 5
    p = GPIO.PWM(channel, frequency)
    p.start(30)
    while not e.is_set():
        for duty_cycle in range(30, 101, step):
            p.ChangeDutyCycle(duty_cycle)
            time.sleep(speed)
        for duty_cycle in range(100, 29, -step):
            p.ChangeDutyCycle(duty_cycle)
            time.sleep(speed)
    p.stop()


def setup():
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(red_pin, GPIO.OUT)
    GPIO.setup(green_pin, GPIO.OUT)
    GPIO.setup(blue_pin, GPIO.OUT)


def off():
    GPIO.output(red_pin, GPIO.LOW)
    GPIO.output(green_pin, GPIO.LOW)
    GPIO.output(blue_pin, GPIO.LOW)


def red():
    GPIO.output(red_pin, GPIO.HIGH)


def green():
    GPIO.output(green_pin, GPIO.HIGH)


def blue():
    GPIO.output(blue_pin, GPIO.HIGH)


def yellow():
    red()
    green()


def cyan():
    blue()
    green()


def magenta():
    red()
    blue()


def white():
    red()
    green()
    blue()
