import asyncio
import logging
import functools

log = logging.getLogger(__name__)


DEFAULT_COMMAND = 'cu -l {device} -s {baudrate}'


def list():
    pass


class Serial:
    def __init__(
            self,
            device='',
            baudrate=115200,
            timeout=1.0,
            command=DEFAULT_COMMAND,
            loop=None):
        self._loop = loop or asyncio.get_event_loop()
        self._device = device
        self._baudrate = baudrate
        self._timeout = timeout
        self._command = command
        self._process = None
        self._send_lock = asyncio.Lock()
        self._tasks = {}

    async def receive(self):
        while True:
            buf = await self._process.stdout.readline()
            log.debug('<< {0}'.format(buf))
            futures = [inbox.put(buf) for inbox in self._tasks.values()]
            log.debug('Forwarding to {0}'.format(futures))
            await asyncio.wait(futures, loop=self._loop)

    async def open(self, timeout=None):
        timeout = timeout if timeout else self._timeout

        task = self._loop.create_task(
            asyncio.create_subprocess_exec(
                *self._command.format(
                    device=self._device,
                    baudrate=self._baudrate).split(' '),
                stdout=asyncio.subprocess.PIPE,
                stdin=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                loop=self._loop))

        self._process = await asyncio.wait_for(task, timeout, loop=self._loop)

    # TODO(artyom, 20170922): consider using context manager
    async def close(self):
        [task.cancel() for task in self._tasks]
        self._process.terminate()
        return await self._process.wait()

    # TODO(artyom, 20170922): this method could implemented
    # as async generator with yield. Need to revisit once we
    # upgrade to Python 3.6
    def monitor(match):
        async def matcher(match, outbox, inbox):
            buf += await queue.get()

            if match(buf):
                log.debug('Monitor {0} matched: {0}'.format(match, buf))
                await outbox.put(buf)
                buf = ''

        outbox = async.Queue(loop=self._loop)
        task, _ = self._create_task(
            functools.partial(matcher(match, outbox)))

        log.debug('Added monitor: {0}'.format(match))

        return task, outbox

    async def send(data, ok, error, timeout=None):
        timeout = timeout if timeout else self._timeout

        async def matcher(ok, error, inbox):
            buf = ''
            while True:
                buf += await inbox.get()

                if ok(buf):
                    return buf

                if error(buf):
                    raise Exception('Received: {0}'.format(buf))

        log.debug('send(): acquiring lock')
        with (await self._send_lock):
            log.debug('send(): lock acquired')
            try:
                task, _ = self._create_task(
                    functools.partial(matcher(ok, error)))
                log.debug('>> ', data)
                self._process.stdin.write(data)
                log.debug('done')
            except Exception as e:
                task.set_exception(e)
                log.error('While writing: ', e)
            else:
                return await asyncio.wait_for(task, timeout, loop=self._loop)

    def _create_task(func):
        def task_done(future):
            del self._tasks[task]

        inbox = asyncio.Queue(loop=self._loop)
        task = self._loop.create_task(func(inbox))
        self._tasks[task] = inbox
        task.add_done_callback(task_done)

        log.debug('Created task {task} for {func} with inbox {inbox}'.format(
                task=task,
                func=func,
                inbox=inbox
            ))

        return task, inbox
