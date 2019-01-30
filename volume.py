"""
The daemon responsible for changing the volume in response to a turn
of the volume knob.
See: https://gist.github.com/thijstriemstra/6396142f426aeffb0c1c6507fb2acd7b
"""

import logging
import signal
import subprocess
import sys
import time

import Adafruit_MCP3008

from config import VOLUME as CONF

# LOGGING
# ========

logger = logging.getLogger(__name__)

# logging
# logging.basicConfig(
#     level=logging.DEBUG,
#     format='%(asctime)-15s - %(message)s'
# )

# SETTINGS
# ========

DEBUG = False

# Software SPI configuration.
GPIO_CLK = CONF.GPIO_CLK
GPIO_MISO = CONF.GPIO_MISO
GPIO_MOSI = CONF.GPIO_MOSI
GPIO_CS = CONF.GPIO_CS

# MCP3008 channel where potentiometer is connected
MCP3008_CHANNEL = CONF.MCP3008_CHANNEL

# The minimum and maximum volumes, as percentages.
#
# The default max is less than 100 to prevent distortion. The default min is
# greater than zero because if your system is like mine, sound gets
# completely inaudible _long_ before 0%. If you've got a hardware amp or
# serious speakers or something, your results will vary.
VOLUME_MIN = CONF.VOLUME_MIN
VOLUME_MAX = CONF.VOLUME_MAX

# The amount you want one click of the knob to increase or decrease the
# volume. I don't think that non-integer values work here, but you're welcome
# to try.
VOLUME_INCREMENT = CONF.VOLUME_INCREMENT

# Audio device name, e.g. 'PCM' or 'Master'. Find with: amixer scontrols
DEVICE_NAME = CONF.DEVICE_NAME


# (END SETTINGS)
#


def debug(str):
    if not DEBUG:
        return
    logger.debug(str)


class RotaryEncoder(object):
    """
    A class to decode mechanical rotary encoder pulses.
    """

    def __init__(self, gpio_CLK, gpio_CS, gpio_MISO, gpio_MOSI, channel, tolerance=10):
        # MCP3008 component
        self.mcp = Adafruit_MCP3008.MCP3008(clk=gpio_CLK, cs=gpio_CS,
                                            miso=gpio_MISO, mosi=gpio_MOSI)
        self.volume = Volume()
        self.channel = channel

        # to keep from being jittery we'll only change
        # volume when the pot has moved more than 5 'counts'
        self.tolerance = tolerance

        # this keeps track of the last potentiometer value
        self.last_read = 0

    def destroy(self):
        debug('Destroying...')

    def read(self):
        # we'll assume that the pot didn't move
        trim_pot_changed = False

        # read the analog pin
        trim_pot = self.mcp.read_adc(self.channel)

        # how much has it changed since the last read?
        pot_adjust = abs(trim_pot - self.last_read)

        if pot_adjust > self.tolerance:
            trim_pot_changed = True

        if trim_pot_changed:
            # convert 10bit adc0 (0-1024) trim pot read into 0-100 volume level
            set_volume = int(round(trim_pot / 10.24))
            self.volume.set_volume(set_volume)

            # save the potentiometer reading for the next loop
            self.last_read = trim_pot


class VolumeError(Exception):
    pass


class Volume(object):
    """
    A wrapper API for interacting with the volume settings on the RPi.
    """
    MIN = VOLUME_MIN
    MAX = VOLUME_MAX
    INCREMENT = VOLUME_INCREMENT

    def __init__(self):
        # Set an initial value for last_volume in case we're muted when we start.
        self.last_volume = self.MIN
        self._sync()

    def up(self):
        """
        Increases the volume by one increment.
        """
        return self.change(self.INCREMENT)

    def down(self):
        """
        Decreases the volume by one increment.
        """
        return self.change(-self.INCREMENT)

    def change(self, delta):
        v = self.volume + delta
        v = self._constrain(v)
        return self.set_volume(v)

    def set_volume(self, v):
        """
        Sets volume to a specific value.
        """
        self.volume = self._constrain(v)
        debug("set volume: {}".format(self.volume))

        output = self.amixer("set '{}' unmute {}%".format(DEVICE_NAME, v))
        self._sync(output)
        return self.volume

    def toggle(self):
        """
        Toggles muting between on and off.
        """
        if self.is_muted:
            output = self.amixer("set '{}' unmute".format(DEVICE_NAME))
        else:
            # We're about to mute ourselves, so we should remember the last volume
            # value we had because we'll want to restore it later.
            self.last_volume = self.volume
            output = self.amixer("set '{}' mute".format(DEVICE_NAME))

        self._sync(output)
        if not self.is_muted:
            # If we just unmuted ourselves, we should restore whatever volume we
            # had previously.
            self.set_volume(self.last_volume)
        return self.is_muted

    def status(self):
        if self.is_muted:
            return "{}% (muted)".format(self.volume)
        return "{}%".format(self.volume)

    # Read the output of `amixer` to get the system volume and mute state.
    #
    # This is designed not to do much work because it'll get called with every
    # click of the knob in either direction, which is why we're doing simple
    # string scanning and not regular expressions.
    def _sync(self, output=None):
        if output is None:
            output = self.amixer("get '{}'".format(DEVICE_NAME))

        lines = output.readlines()
        if DEBUG:
            strings = [line.decode('utf8') for line in lines]
            debug("OUTPUT:")
            debug("".join(strings))
        last = lines[-1].decode('utf-8')

        # The last line of output will have two values in square brackets. The
        # first will be the volume (e.g., "[95%]") and the second will be the
        # mute state ("[off]" or "[on]").
        i1 = last.rindex('[') + 1
        i2 = last.rindex(']')

        self.is_muted = last[i1:i2] == 'off'

        i1 = last.index('[') + 1
        i2 = last.index('%')
        # In between these two will be the percentage value.
        pct = last[i1:i2]

        self.volume = int(pct)

    # Ensures the volume value is between our minimum and maximum.
    def _constrain(self, v):
        if v < self.MIN:
            return self.MIN
        if v > self.MAX:
            return self.MAX
        return v

    def amixer(self, cmd):
        p = subprocess.Popen("amixer {}".format(cmd), shell=True, stdout=subprocess.PIPE)
        code = p.wait()
        if code != 0:
            raise VolumeError("Unknown error: {}".format(code))
            sys.exit(0)

        return p.stdout


if __name__ == "__main__":
    def on_exit(a, b):
        debug("Exiting...")
        encoder.destroy()
        sys.exit(0)


    debug("Volume knob using pins GPIO_CLK ({}), GPIO_CS ({}), GPIO_MISO ({}) and GPIO_MOSI ({})".format(
        GPIO_CLK, GPIO_CS, GPIO_MISO, GPIO_MOSI))

    encoder = RotaryEncoder(GPIO_CLK, GPIO_CS, GPIO_MISO, GPIO_MOSI, MCP3008_CHANNEL)
    signal.signal(signal.SIGINT, on_exit)

    debug("Initial volume: {}".format(encoder.volume.volume))

    while True:
        encoder.read()

        # hang out and do nothing for a half second
        time.sleep(0.05)
