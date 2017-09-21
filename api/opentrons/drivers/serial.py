import asyncio
import logging

log = logging.getLogger(__name__)


DEFAULT_COMMAND = 'cu -l {device} -s {baudrate}'


def list():
    pass


class Serial(object):
    def __init__(self,
                 device='',
                 baudrate=115200,
                 timeout=1.0,
                 command=DEFAULT_COMMAND,
                 loop=None):
        self._loop = loop or asyncio.get_event_loop()
        self._port = port
        self._baudrate = baudrate
        self._timeout = timeout
        self._command = command
        self._process = None
        self._send_queue = asyncio.Queue(loop=self._loop)

    async def send_task(self):
        while True:
            data, ok, error, event, receive_queue = \
                await self._send_queue.get()
            self._process.stdin.write(data.encode())

            yield from stream.readline()
            # read until matcher is True

    async def open(self, timeout=None):
        timeout = timeout if timeout else self._timeout

        task = self._loop.create_task(asyncio.create_subprocess_exec(
            self._command.format(device=self._device, baudrate=self._baudrate),
            stdout=asyncio.subprocess.PIPE,
            stdin=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE))

        return asyncio.wait(task, timeout).result()

    def close(self):
        pass

    async def send(data, ok, error, event=None, timeout=None):
        timeout = timeout if timeout else self._timeout
        receive_queue = asyncio.Queue(loop=self._loop)
        task, receive_queue = self._send(data, ok, error, event)
        self._send_queue.put((data, ok, error, event, receive_queue))
