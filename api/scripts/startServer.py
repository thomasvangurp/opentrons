from opentrons import server

if __name__ == '__main__':
    print("[BOOT] Server node setup")
    server.start('0.0.0.0')
    print("[BOOT] Server node terminated")
