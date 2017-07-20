#!/usr/bin/env python

# lighting pattern when both wifi and smoothie are connected
import os, time, sys
import time
import piglow
import threading
import boot_config as bc

def wifi_connected_smoothie_connected():
    for x in range(210, 240):
        piglow.green(x)
        # piglow.white(x - 190)
        piglow.show()
        time.sleep(0.05)
    for x in range(240, 210, -1):
        piglow.green(x)
        # piglow.white(x - 190)
        piglow.show()
        time.sleep(0.05)

# indicates hardware issue
def issue():
    piglow.red(200)
    piglow.show()
    time.sleep(0.4)
    piglow.red(20)
    piglow.show()
    time.sleep(0.4)



def access_point():
    for x in range(140, 250, 2):
        piglow.blue(x)
        piglow.show()
        time.sleep(0.01)
    for x in range(250, 140, -2):
        piglow.blue(x)
        piglow.show()
        time.sleep(0.01)

def status_checker():
    global STATUS
    os.mkfifo(bc.STATUS_INDICATOR_FIFO)
    with open(bc.STATUS_INDICATOR_FIFO, 'r') as status_file:
        print('1\n')
        while True: 
            print('2\n')
            received_status = status_file.readline()
            print('3\n')

            try:
                STATUS = int(received_status)
            except ValueError:
                print('4\n')
                continue
            print('5\n')
            piglow.off()
            print('[STATUS LIGHT] Status change: ', STATUS)

def status_responder():
    global STATUS
    boot_counter = 0
    while True:
        if STATUS == bc.BOOTING:
            booting()
        elif STATUS == bc.WIFI_AND_SMOOTHIE_CONNECTED:
            wifi_connected_smoothie_connected()
        elif STATUS == bc.ACCESS_POINT:
            access_point()
        elif STATUS == bc.ISSUE:
            issue()
        else:
            boot_counter += 1
            if boot_counter > 1000:
                piglow.off()
                STATUS = bc.ISSUE

if __name__ == "__main__":
    STATUS = None

    threading.Thread(target=status_checker).start()
    threading.Thread(target=status_responder).start()




