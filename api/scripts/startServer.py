from opentrons import server, robot

DEFAULT_PORT = '/dev/ttyACM0'

if __name__ == '__main__':
    print("[BOOT] Server node setup")
    robot.connect(DEFAULT_PART)
    server.start('0.0.0.0')
    print("[BOOT] Server node terminated")
