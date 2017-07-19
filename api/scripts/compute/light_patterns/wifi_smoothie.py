#!/usr/bin/env python

# lighting pattern when both wifi and smoothie are connected

import time
import piglow



def wifi_connected_smoothie_connected():
    piglow.off()
    while True:
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
def hardware_issue():
    piglow.off()
    while True:
        piglow.red(200)
        piglow.show()
        time.sleep(0.4)
        piglow.red(20)
        piglow.show()
        time.sleep(0.4)



def access_point():
    piglow.off()
    while True:
        for x in range(140, 250, 2):
            piglow.blue(x)
            piglow.show()
            time.sleep(0.01)
        for x in range(250, 140, -2):
            piglow.blue(x)
            piglow.show()
            time.sleep(0.01)