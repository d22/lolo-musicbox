class BUTTON:
    # GPIO Pins, mode GPIO.BOARD
    PAUSE_PIN = 13
    NEXT_PIN = 15
    PREV_PIN = 11
    POWER_PIN = 5
    # button press timeout, dead time before a button press
    # can be registered again
    TIMEOUT = 0.5
    # how long the power button has to be pressed before
    # the raspi is shutdown
    POWER_PRESS_TIME = 5


class LED:
    # Power LED is Pin 8 ()
    # GPIO Pins, mode GPIO.BOARD
    RED_PIN = 32
    GREEN_PIN = 36
    BLUE_PIN = 38

    BLINK_SLEEP = 0.8


class PATHS:
    # make sure this matches the music_directory in /etc/mpd.conf
    # directory must exist
    MUSIC_DIR = '/home/pi/music/'
    # directory must exist
    MOUNT_DIR = '/media/usb_stick'
    # name of the music directory on the usb stick (all mp3 in this dir will be copied)
    MUSIC_SRC_DIR = 'lolo'


class USB:
    # number of lines of the output of 'sudo lsusb'
    # without any usb device connected
    DEFAULT_LSUSB_LINES = 4


class VOLUME:
    # see: https://learn.adafruit.com/raspberry-pi-analog-to-digital-converters/mcp3008
    # and: https://gist.github.com/thijstriemstra/6396142f426aeffb0c1c6507fb2acd7b
    # GPIO Pins, mode GPIO.BCM
    GPIO_CLK = 5  # 29 GPIO.BOARD
    GPIO_MISO = 6  # 31 GPIO.BOARD
    GPIO_MOSI = 13  # 33 GPIO.BOARD
    GPIO_CS = 19  # 35 GPIO.BOARD
    # MCP3008 channel where potentiometer is connected
    MCP3008_CHANNEL = 7
    # The minimum and maximum volumes, as percentages.
    #
    # The default max is less than 100 to prevent distortion. The default min is
    # greater than zero because if your system is like mine, sound gets
    # completely inaudible _long_ before 0%. If you've got a hardware amp or
    # serious speakers or something, your results will vary.
    VOLUME_MIN = 25
    VOLUME_MAX = 95
    # The amount you want one click of the knob to increase or decrease the
    # volume. I don't think that non-integer values work here, but you're welcome
    # to try.
    VOLUME_INCREMENT = 1
    # Audio device name, e.g. 'PCM' or 'Master'. Find with: amixer scontrols
    DEVICE_NAME = 'PCM'


class SOUNDEFFECTS:
    DIR = '/home/pi/lolo/sounds/'
    PLING = 'pling-new.mp3'
    CLIC = 'clic.mp3'
    PRING_DOWN = 'prrring-down-short.mp3'
    PRING_UP = 'prrring-up-short.mp3'
    ZURR = 'zurr.mp3'


class LOGGER:
    LOG_FILE = '/home/pi/lolo/logs/lolo.log'
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_DATE_FORMAT = '%y-%m-%d %H:%M:%S'
