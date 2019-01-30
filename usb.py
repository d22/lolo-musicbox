import logging
import subprocess

from config import PATHS
from config import USB

log = logging.getLogger(__name__)


def run_command(command):
    result = subprocess.check_output(command, shell=True)
    return result.decode('utf8')


def uuid_from_line(line):
    start_str = "UUID=\""
    example_uuid = "6784-3407"
    uuid_start = line.index(start_str) + len(start_str)
    uuid_end = uuid_start + len(example_uuid)
    return line[uuid_start: uuid_end]


def has_usb_stick():
    output = run_command("sudo lsusb | wc -l")
    return int(output) > USB.DEFAULT_LSUSB_LINES


def auto_mount():
    log.info('attempt automount')
    output = run_command("sudo blkid | grep LABEL | grep -v boot | grep -v rootfs").splitlines()
    log.debug('output: ' + str(output))
    # ['/dev/sda1: LABEL="KINGSTON" UUID="6784-3407" TYPE="vfat" PARTUUID="459720e1-01"']
    for usb_device in output:
        if isinstance(usb_device, int):
            continue
        log.info('usb_device: ' + usb_device)
        command = "sudo mount --uuid %s %s" % (uuid_from_line(usb_device), PATHS.MOUNT_DIR)
        run_command(command)
        break


def umount():
    run_command("sudo umount " + PATHS.MOUNT_DIR)


if __name__ == "__main__":
    auto_mount()
