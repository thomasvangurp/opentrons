#!/usr/bin/env python

from opentrons import server, robot
from status_light import send_status
import os, time

DEFAULT_PORT = '/dev/ttyACM0'

if __name__ == '__main__':
    try:
        print("[SERVER BOOT] Server node setup")
        try:
            robot.connect(DEFAULT_PORT)
            send_status({'SMOOTHIE_CONNECTED': True})
        except RuntimeError:
            # Sometimes it fails on the first connection attempt - not sure why.
            # TODO: Change this hackey fix
            robot.connect(DEFAULT_PORT)
            print("[SERVER BOOT] Second smoothie connect attempt")
            send_status({'SMOOTHIE_CONNECTED': True})
        except FileNotFoundError:
            send_status({'SMOOTHIE_CONNECTED': False})
            print("[SERVER ERROR] No smoothie detected at ", DEFAULT_PORT)
        except:
            send_status({'SMOOTHIE_CONNECTED': False})
            send_status({'ISSUE': True})

        send_status({'SERVER_ONLINE': True})
        server.start('0.0.0.0')
        send_status({'SERVER_ONLINE': False})



        print("[SERVER SHUTDOWN] Server node terminated")
    
    # The server above should run indefinitely 
    finally:
        send_status({'ISSUE': True})





