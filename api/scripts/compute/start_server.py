#!/usr/bin/env python

from opentrons import server, robot
import boot_config as bc
import os, time

if __name__ == '__main__':
    print("[SERVER BOOT] Opening status indication pipe")
    fd = os.open(bc.STATUS_INDICATOR_FIFO, os.O_WRONLY) 
    os.write(fd, str(bc.BOOTING).encode())

    try:
        print("[SERVER BOOT] Server node setup")
        try:
            robot.connect(bc.DEFAULT_PORT)
        except RuntimeError:
            # Sometimes it fails on the first connection attempt - not sure why.
            # TODO: Change this hackey fix
            print("[SERVER BOOT] Second smoothie connect attempt")
            robot.connect(bc.DEFAULT_PORT)
        except FileNotFoundError:


        os.write(fd, str(bc.WIFI_AND_SMOOTHIE_CONNECTED).encode()) 
        server.start('0.0.0.0')
        print("[SERVER SHUTDOWN] Server node terminated")
    
    # The server above should run indefinitely 
    finally:
        os.write(fd, str(bc.ISSUE).encode()) 
