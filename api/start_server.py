from opentrons import server
import RPi.GPIO as GPIO
import time
import subprocess

def network_name():
    SSID = None
    try:
        SSID = subprocess.check_output(["iwgetid", "-r"]).strip()
    except subprocess.CalledProcessError: 
        pass
    return SSID


def access_point_setup():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(18, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    if not network_name():
        subprocess.call(["node", "resin-wifi-connect/src/app.js", "--clear=true"])

def listen_for_reset()
    counter = 0
    while True:
        input_state = GPIO.input(18)
        if input_state == False:
            counter = counter + 1
            time.sleep(.5)
        else:
            counter = 0

        #if button has been held for 2 seconds 
        if count == 4:
            print("Connection Configuration Reset")
            subprocess.call(["node", "resin-wifi-connect/src/app.js", "--clear=true"])


if __name__ == '__main__':
    access_point_setup()
    server.start('0.0.0.0')
