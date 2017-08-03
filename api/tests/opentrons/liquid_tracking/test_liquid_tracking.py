import unittest

from opentrons import robot
from opentrons.containers import load as containers_load
from opentrons.instruments import pipette
from pytest import approx
from math import pi


def test_liquid_tracking():
    from opentrons.tracker import Tracker

    trash = containers_load(robot, 'point', 'A1')
    tiprack1 = containers_load(robot, 'tiprack-10ul', 'B2')
    plate = containers_load(robot, '96-flat', 'A2')
    trough = containers_load(robot, 'point', 'A3')

    p200 = pipette.Pipette(
        robot,
        axis="b",
        trash_container=trash,
        tip_racks=[tiprack1],
        max_volume=200,
        min_volume=10,  # These are variable
        channels=1,
        name='other-pipette-for-transfer-tests'
    )

    tracker = Tracker(instruments=[p200], state={
        trough: {'red': 30, 'blue': 30}
    })

    # Using approx to compare floating point numbers
    # More here: https://docs.pytest.org/en/latest/builtin.html#comparing-floating-point-numbers  # NOQA

    p200.aspirate(60, trough)
    assert trough.volume == approx(0)

    p200.dispense(30, plate['A1'])
    assert plate['A1'].volume == approx(30)
    assert plate['A1'].liquids == approx({'red': 15, 'blue': 15})
    assert plate['A1'].concentrations == approx({'red': 0.5, 'blue': 0.5})

    p200.dispense(30, plate['A2'])
    assert plate['A2'].volume == approx(30)
    assert plate['A2'].liquids == approx({'red': 15, 'blue': 15})
    assert plate['A2'].concentrations == approx({'red': 0.5, 'blue': 0.5})

    d = plate['A1'].properties['diameter']
    h = plate['A1'].volume / (pi * d * d / 4)

    # TODO: make sure h value aligns with measurement units for
    # dimensions (mm) and volume (uL).
    assert h == approx(2)  # 2.0 is an arbitrary number to set off an assertion
