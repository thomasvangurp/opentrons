#!/usr/bin/env python

# lighting pattern when both wifi and smoothie are connected
import os, time, sys
import time
import piglow
import asyncio

async def booting():
    freq = 0.4
    piglow.all(0)
    while True:
        for x in range(100, 240):
            piglow.white(x)
            piglow.show()
            await asyncio.sleep(freq)
        for x in range(240, 100, -1):
            piglow.white(x)
            piglow.show()
            await asyncio.sleep(freq)

async def fully_connected():
    freq = 0.4
    piglow.all(0)
    while True:
        for x in range(100, 240):
            piglow.green(x)
            piglow.show()
            await asyncio.sleep(freq)
        for x in range(240, 100, -1):
            piglow.green(x)
            piglow.show()
            await asyncio.sleep(freq)

# indicates issue 
async def issue():
    freq = 0.4
    piglow.all(0)
    while True:
        piglow.red(200)
        piglow.show()
        await asyncio.sleep(freq)
        piglow.red(20)
        piglow.show()
        await asyncio.sleep(freq)

async def access_point():
    i = 0
    freq = 0.1

    while True:
        piglow.all(0)
        piglow.set(i % 18, [15, 31, 63, 127, 255, 127, 63, 31, 15])
        piglow.show()
        i += 1
        await asyncio.sleep(freq)

statuses = {
    'BOOTING': booting,
    'ACCESS_POINT': access_point,
    'FULLY_CONNECTED': fully_connected,
    'ISSUE': issue
}   

class RobotStatusChangeError(NotImplementedError):
    """Raised when an invalid status change is requested for the
    robot status lights.

    Attributes:
        received status -- status received
    """

    def __init__(self, received_status):
        self.received_status = received_status
        
def create_listener():
    current_animation = None
    prev_state = None

    async def listen(reader, writer):
        def cancel_animation():
            if current_animation:
                current_animation.cancel()
        def set_state(lighting_function):
            nonlocal current_animation
            cancel_animation()
            current_animation = loop.create_task(lighting_function())

        nonlocal prev_state
        data = await reader.readline()
        new_state = data.decode()
        addr = writer.get_extra_info('peername')
        print("Received %r from %r" % (new_state, addr))

        if new_state in statuses:
            prev_state = new_state
            set_state(statuses[new_state])
        else:
            print('No animation for state: {}. Ignoring.'.format(new_state))
            raise(RobotStatusChangeError(data))
        writer.close() # Is this necessary? Why here? Does the reader need to be closed?
    return listen

def send_status(status):
    async def tcp_writer(message, loop):
        reader, writer = await asyncio.open_connection('127.0.0.1', 8888,
                                                   loop=loop)
        print('Send: %r' % message)
        writer.write(message)
        print('Close the socket')
        writer.close()
    loop = asyncio.get_event_loop()
    status_to_send = (str(status) + '\n').encode()
    loop.run_until_complete(tcp_writer(str(status).encode(), loop))


if __name__ == "__main__":

    try:
        loop = asyncio.get_event_loop()
        coro = asyncio.start_server(
            create_listener(), '127.0.0.1', 8888, loop=loop)
        server = loop.run_until_complete(coro)

        print('Serving on {}'.format(server.sockets[0].getsockname()))
        try:
            loop.run_forever()
        except KeyboardInterrupt:
            pass

        # Close the server
        server.close()
        loop.run_until_complete(server.wait_closed())
        loop.close()
    finally:
        piglow.off()


