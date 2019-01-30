#!/usr/bin/env bash

# install required system packages
sudo apt-get update
sudo apt-get upgrade
sudo apt-get install -y python3 python3-pip mpd mpc mpg123

# install required python packages
pip3 install -r requirements.txt

# create directories
sudo mkdir -p /media/usb_stick
mkdir ~/music

# mpd config (make sure this matches the music dir in config.py)
sudo sed -i "s@music_directory.*@music_directory \"$HOME/music\"@g" /etc/mpd.conf
sudo sed -i "s@#.*device.*hw:0,0.*@device \"hw:0,0\"@g" /etc/mpd.conf

# install services
sudo systemctl enable ~/lolo/services/volume.service
sudo systemctl enable ~/lolo/services/lolo.service

sudo systemctl start volume
sudo systemctl start lolo

# disable unneeded services (boot faster)
sudo systemctl disable ntp.service
sudo systemctl disable dphys-swapfile.service
sudo systemctl disable keyboard-setup.service
sudo systemctl disable apt-daily.service
sudo systemctl disable wifi-country.service
sudo systemctl disable hciuart.service
sudo systemctl disable raspi-config.service
sudo systemctl disable avahi-daemon.service
sudo systemctl disable triggerhappy.service

# remove plymouth (boot faster)
sudo apt-get purge --remove plymouth

# install boot config
sudo mv /boot/config.txt /boot/config.txt.orig
sudo cp boot-config.txt /boot/config.txt
