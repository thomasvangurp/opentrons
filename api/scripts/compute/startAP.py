import RPi.GPIO as GPIO
import time
import subprocess
import os



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
    listen_for_reset()

def listen_for_reset():
    counter = 0
    while True:
        input_state = GPIO.input(18)
        if input_state == False:
            counter = counter + 1
            time.sleep(.5)
        else:
            counter = 0

        #if button has been held for 2 seconds 
        if counter == 4:
            print("Connection Configuration Reset")
            os.write(fd, str(bc.BOOT).encode())
            subprocess.call(["node", "resin-wifi-connect/src/app.js", "--clear=true"])


if __name__ == '__main__':
    fd = os.open(bc.STATUS_INDICATOR_FIFO, os.O_WRONLY) 
    print("[BOOT] AP node setup")
    access_point_setup()
    print("[SHUTDOWN] AP node terminated")
