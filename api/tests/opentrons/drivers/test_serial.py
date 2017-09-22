#!/bin/env python

import pytest
from opentrons.drivers import Serial


@pytest.fixture
async def serial(loop, request):
    instance = Serial(
        device='/dev/echo',
        baudrate=2400,
        command='test_serial.py {device} {baudrate}',
        timeout=0.5,
        loop=loop)

    await instance.open()

    def finalizer():
        instance.close()

    request.addfinalizer(finalizer)
    return instance


def test_open_close(serial):
    pass
