#!/usr/bin/env python

# lighting pattern when both wifi and smoothie are connected
import os, time, sys
import time
import piglow
import asyncio

statuses = {
    'BOOTING': 0,
    'ACCESS_POINT': 1,
    'WIFI_AND_SMOOTHIE_CONNECTED': 2,
    'ISSUE': 3
}            


async def fully_connected():
    freq = 0.4
    piglow.all(0)
    for x in range(210, 240):
        piglow.green(x)
        piglow.show()
        await asyncio.sleep(freq)
    for x in range(240, 210, -1):
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
    freq = 0.01
    piglow.all(0)
    while True:
        for x in range(140, 250, 2):
            piglow.blue(x)
            piglow.show()
            await asyncio.sleep(freq)
        for x in range(250, 140, -2):
            piglow.blue(x)
            piglow.show()
            await asyncio.sleep(freq)

def create_listener():
    current_animation = None
    prev_state = None

    async def listen(reader, writer):
        nonlocal current_animation
        nonlocal prev_state
        loop = asyncio.get_event_loop()

        def cancel_animation():
            if current_animation:
                current_animation.cancel()

        def set_state(lighting_function):
            cancel_animation()
            current_animation = loop.create_task(booting)
            new_state = prevState

        data = await reader.readline()
        try:
            new_state = int(data)
        except ValueError:
            print('[ERROR] received a non-interger status code\n')
        addr = writer.get_extra_info('peername')
        print("Received %r from %r" % (new_state, addr))

        prev_state = new_state

        if new_state == statuses['BOOTING']:
            set_state(booting)
        elif new_state == statuses['WIFI_AND_SMOOTHIE_CONNECTED']:
            set_state(fully_connected)
        elif new_state == statuses['ACCESS_POINT']:
            set_state(access_point)
        elif new_state == statuses['ISSUE']:
            set_state(issue)
        else:
            print('No animation for state: {}. Ignoring.'.format(new_state))

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
    loop.run_until_complete(tcp_writer(status, loop))
    loop.close()


if __name__ == "__main__":
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



