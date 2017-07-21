#!/usr/bin/env python

from opentrons import server, robot
from status_light import send_status
import os, time

DEFAULT_PORT = '/dev/ttyACM0'

if __name__ == '__main__':
    send_status('BOOTING')

    try:
        print("[SERVER BOOT] Server node setup")
        try:
            robot.connect(DEFAULT_PORT)
        except RuntimeError:
            # Sometimes it fails on the first connection attempt - not sure why.
            # TODO: Change this hackey fix
            print("[SERVER BOOT] Second smoothie connect attempt")
            robot.connect(DEFAULT_PORT)
        except FileNotFoundError:
            print("[SERVER ERROR] No smoothie detected at ", DEFAULT_PORT)

        server.start('0.0.0.0')
        print("[SERVER SHUTDOWN] Server node terminated")
    
    # The server above should run indefinitely 
    finally:
        send_status('ISSUE')





