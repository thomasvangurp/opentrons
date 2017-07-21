#!/usr/bin/env python

import RPi.GPIO as GPIO
import time
import subprocess
import os
from status_light import send_status
def network_name():
    SSID = None
    try:
        SSID = subprocess.check_output(["iwgetid", "-r"]).strip()
    except subprocess.CalledProcessError: 
        pass
    return SSID


def network_check():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(21, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    if not network_name():
        send_status({'WIRELESS_NETWORK_CONNECTED': False, 'ACCESS_POINT': True})
        subprocess.call(["node", "resin-wifi-connect/src/app.js", "--clear=true"])
        send_status({'WIRELESS_NETWORK_CONNECTED': True, 'ACCESS_POINT': False})
    listen_for_reset()

def listen_for_reset():
    counter = 0
    while True:
        input_state = GPIO.input(21)
        if input_state == False:
            counter = counter + 1
            time.sleep(.5)
        else:
            counter = 0

        #if button has been held for 2 seconds 
        if counter == 4:
            print("Connection Configuration Reset")
            send_status({'WIRELESS_NETWORK_CONNECTED': False, 'ACCESS_POINT': True})
            subprocess.call(["node", "resin-wifi-connect/src/app.js", "--clear=true"])
            send_status({'WIRELESS_NETWORK_CONNECTED': True, 'ACCESS_POINT': False})




if __name__ == '__main__':

    print("[BOOT] AP node setup")
    network_check()
    print("[SHUTDOWN] AP node terminated")
