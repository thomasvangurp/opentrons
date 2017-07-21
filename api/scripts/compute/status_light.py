#!/usr/bin/env python

# lighting pattern when both wifi and smoothie are connected
import os, time, sys
import time
import piglow
import asyncio
import json



async def access_point():
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


# indicates unknown state. This should never be encountered
# but is here to prevent an else statement in derive_state()
# that maps to a known set of state parameters since this 
# would be a very misleading bug 
async def unknown_state():
    freq = 0.05
    piglow.all(0)
    while True:
        piglow.red(200)
        piglow.show()
        await asyncio.sleep(freq)
        piglow.red(20)
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

async def booting():
    i = 0
    freq = 0.1

    while True:
        piglow.all(0)
        piglow.set(i % 18, [15, 31, 63, 127, 255, 127, 63, 31, 15])
        piglow.show()
        i += 1
        await asyncio.sleep(freq)

states = {
    'booting': booting,
    'access_point': access_point,
    'fully_connected': fully_connected,
    'issue': issue,
    'unknown': unknown_state
}   


# defines state precedence
def derive_state(state_components):
    lighting_coroutine_function = None
    if state_components['ISSUE']:
        lighting_coroutine_function = states['issue']
    elif state_components['ACCESS_POINT']:
        lighting_coroutine_function = states['access_point']
    elif (state_components['SERVER_ONLINE'] and 
            state_components['SMOOTHIE_CONNECTED'] and
            state_components['WIRELESS_NETWORK_CONNECTED']):
        lighting_coroutine_function = states['fully_connected']
    elif state_components['BOOTING']:
        lighting_coroutine_function = states['booting']
    else:
        lighting_coroutine_function = states['unknown']

    print("STATE RESOLVED TO: ", lighting_coroutine_function)
    return lighting_coroutine_function


class RobotLightIndicatorStateError(Exception):
    """Raised when the lights that indicate robot state
    are places in an invalid state. Most likely means that 
    invalid state_component parameters were sent by other processes.

    Attributes:
        received status -- status received
    """

    def __init__(self, received_status):
        self.received_status = received_status
        
def create_listener():
    current_animation = None

    state_components = {
        'WIRELESS_NETWORK_CONNECTED': False,
        'ACCESS_POINT': False,
        'SMOOTHIE_CONNECTED': False,
        'ISSUE': False,
        'BOOTING': True,
        'SERVER_ONLINE': False
    }

    async def listen(reader, writer):
        nonlocal state_components
        def cancel_animation():
            if current_animation:
                current_animation.cancel()
        def set_state(lighting_function):
            nonlocal current_animation
            cancel_animation()
            current_animation = loop.create_task(lighting_function())

        data = await reader.readline()
        new_states = json.loads(data.decode())
        print(new_states)
        
        new_state_components = {**state_components, **new_states} # 3.5 syntax for dict merge
        if not len(new_state_components) == len(state_components):
            raise(RobotStatusChangeError(new_states))
        else:
            state_components = new_state_components

        addr = writer.get_extra_info('peername')
        print("Received %r from %r" % (new_states, addr))
        set_state(derive_state(state_components))
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
    status_to_send = (json.dumps(status) + '\n').encode()
    loop.run_until_complete(tcp_writer(status_to_send, loop))


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


