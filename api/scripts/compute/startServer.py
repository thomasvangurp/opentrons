from opentrons import server, robot

DEFAULT_PORT = '/dev/ttyACM0'

if __name__ == '__main__':
    print("[BOOT] Server node setup")
    try:
        robot.connect(DEFAULT_PORT)
    except RuntimeError:
        # Sometimes it fails on the first connection attempt - not sure why.
        # TODO: Change this hackey fix
        print("[BOOT] Second smoothie connect attempt")
        robot.connect(DEFAULT_PORT)
    server.start('0.0.0.0')
    print("[BOOT] Server node terminated")

