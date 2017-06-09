from pprint import pprint
import pytest
from opentrons import Robot, instruments, containers


def get_robot():
    r = Robot.get_instance()
    r.reset()
    r.clear_commands()

    trough = containers.load('trough-12row', 'A1', 'trough')
    plate = containers.load('96-flat', 'A2', 'plate')
    p200 = instruments.Pipette(axis='a', name='p200', max_volume=200)

    return r, trough, plate, p200


def test_aspirate():
    r, trough, plate, p200 = get_robot()

    r.set_liquid_state({
        trough['A1']: {'red': 100},
        trough['A2']: {'green': 100},
        trough['A3']: {'blue': 100}
    })

    p200.aspirate(100, trough['A1']).dispense(100, plate['A1'])
    p200.aspirate(100, trough['A2']).dispense(100, plate['A1'])
    p200.aspirate(100, plate['A1']).dispense(100, plate['A2'])

    assert r.get_liquid_state(plate['A1']) == {
        'red': 50,
        'green': 50
    }
    assert r.get_liquid_state(plate['A2']) == {
        'red': 50,
        'green': 50
    }

    r.simulate()
    assert r.get_liquid_state(plate['A1']) == {
        'red': 50,
        'green': 50
    }
    assert r.get_liquid_state(plate['A2']) == {
        'red': 50,
        'green': 50
    }


def test_robot_add_liquids():
    r, trough, plate, p200 = get_robot()

    r.set_liquid_state({
        trough['A1']: {'red': 10000},
        trough['A2']: {'green': 10000},
        trough['A3']: {'blue': 10000}
    })

    assert r.get_liquid_state() == {
        trough['A1']: {'red': 10000},
        trough['A2']: {'green': 10000},
        trough['A3']: {'blue': 10000}
    }

    p200.aspirate(90, trough[0])

    assert r.get_liquid_state() == {
        trough['A1']: {'red': 9910},
        trough['A2']: {'green': 10000},
        trough['A3']: {'blue': 10000},
        'a': {'red': 90}
    }

    p200.dispense(plate[0])

    assert r.get_liquid_state() == {
        trough['A1']: {'red': 9910},
        trough['A2']: {'green': 10000},
        trough['A3']: {'blue': 10000},
        'a': {'red': 0},
        plate['A1']: {'red': 90}
    }

    assert r.get_liquid_state() == {
        trough['A1']: {'red': 9910},
        trough['A2']: {'green': 10000},
        trough['A3']: {'blue': 10000},
        'a': {'red': 0},
        plate['A1']: {'red': 90}
    }

    r.simulate()
    assert r.get_liquid_state() == {
        trough['A1']: {'red': 9910},
        trough['A2']: {'green': 10000},
        trough['A3']: {'blue': 10000},
        'a': {'red': 0},
        plate['A1']: {'red': 90}
    }
