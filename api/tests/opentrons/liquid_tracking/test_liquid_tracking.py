import unittest

from opentrons.util import liquid_functions as lf
from opentrons import robot
from opentrons.containers import load as containers_load
from opentrons.containers import Well
from opentrons.instruments import pipette
from pytest import approx
from math import pi
from opentrons.util import trace



#Remember: Need to test for tracking liquids when they are not defined.
# Planning on hashing the well object ids and, if they as aspirated into,
# just forgetting they had any values??



#TODO: Needed tests -


def well_registers_when_created():
    broker = trace.EventBroker.get_instance()
    objects = broker._tracked_objects
    assert len(objects) == 0
    well = Well()
    assert id(well) in objects

def test_well_registration_from_container_load():
    broker = trace.EventBroker.get_instance()
    objects = broker._tracked_objects
    assert len(objects) == 0

    plate = containers_load(robot, '96-flat', 'A2')
    for well in plate.wells():
        assert id(well) in objects

def adding_liquid_to_well():
    trash = containers_load(robot, 'point', 'A1')
    trash['A1'].add_liquid('green', 10)
    assert trash['A1']._state == \
           {'liquids': {'green': 1}, 'volume': 10}

def test_pipette_aspiration():
    broker = trace.EventBroker.get_instance()
    objects = broker._tracked_objects
    # assert len(objects) == 0 #TODO: Singleton issues in reference deletions
    # plate = containers_load(robot, '96-flat', 'A2')
    print(objects)
    trash = containers_load(robot, 'point', 'A1')
    tiprack1 = containers_load(robot, 'tiprack-10ul', 'B2')
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
    trash['A1'].add_liquid('green', 20)
    p200.aspirate(10, trash['A1'])
    assert p200._state == {'liquids': {'green': 1},
                           'volume': 10}
    trash['A1'].add_liquid('red', 10)
    p200.aspirate(10, trash['A1'])

    assert p200._state == {'liquids': {'green': .75,
                                       'red': .25},
                           'volume': 20}

def test_pipette_dispense():
    broker = trace.EventBroker.get_instance()
    objects = broker._tracked_objects
    plate = containers_load(robot, '96-flat', 'A2')
    trash = containers_load(robot, 'point', 'A1')
    tiprack1 = containers_load(robot, 'tiprack-10ul', 'B2')
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
    trash['A1'].add_liquid('green', 20)
    p200.aspirate(10, trash['A1'])
    assert p200._state == {'liquids': {'green': 1},
                           'volume': 10}
    trash['A1'].add_liquid('red', 10)
    p200.aspirate(10, trash['A1'])

    assert p200._state == {'liquids': {'green': .75,
                                       'red': .25},
                           'volume': 20}
    p200.dispense(10, plate['A1'])
    assert plate['A1']._state == {'liquids': {'red': 0.25, 'green': 0.75}, 'volume': 10}

def test_liquid_tracking():

    trash = containers_load(robot, 'point', 'A1')
    tiprack1 = containers_load(robot, 'tiprack-10ul', 'B2')
    plate = containers_load(robot, '96-flat', 'A2')
    trough = containers_load(robot, 'point', 'A3')

    trough['A1'].add_liquid('red', 30)
    trough['A1'].add_liquid('blue',30)

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

    # Using approx to compare floating point numbers
    # More here: https://docs.pytest.org/en/latest/builtin.html#comparing-floating-point-numbers  # NOQA

    p200.aspirate(60, trough['A1'])
    assert trough['A1']._state['volume'] == approx(0)


    p200.dispense(30, plate['A1'])
    assert plate['A1']._state['volume']  == approx(30)
    assert plate['A1']._state['liquids'] == {'red': 0.5, 'blue': 0.5}

    p200.dispense(30, trough)
    assert trough['A1']._state['volume']  == approx(30)
    assert trough['A1']._state['liquids'] == {'red': 0.5, 'blue': 0.5}

    # p200.dispense(30, plate['A2'])
    # assert plate['A2']._state['volume']  == approx(30)
    # assert plate['A2']._state['liquids'] == approx({'red': 0.5, 'blue': 0.5})


    # d = plate['A1'].properties['diameter']
    # h = plate['A1'].volume / (pi * d * d / 4)

    # TODO: make sure h value aligns with measurement units for
    # dimensions (mm) and volume (uL).
    # assert h == approx(2)  # 2.0 is an arbitrary number to set off an assertion

def dispense_at_liquid():
    trash = containers_load(robot, 'point', 'A1')
    tiprack1 = containers_load(robot, 'tiprack-10ul', 'B2')
    plate = containers_load(robot, '96-flat', 'A2')
    trough = containers_load(robot, 'point', 'A3')

    trough['A1'].add_liquid('red', 30)
    trough['A1'].add_liquid('blue',30)

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

def dispense_at_liquid_level():
    plate = containers_load(robot, 'tube-rack-15_50ml', 'A1')
    p200 = pipette.Pipette(
        robot,
        axis="b",
        max_volume=200,
        min_volume=10,  # These are variable
        channels=1,
        name='pipette'
    )
    p200.motor.move(p200._get_plunger_position('bottom'))
    plate['A4'].add_liquid('green', 500)
    p200.aspirate(100, plate['A4'])
    for i in range(4):
        p200.dispense_at_liquid_level(25, plate['B2'])


dispense_at_liquid_level()
    # adding_liquid_to_well()
    # test_pipette_aspiration()
    # test_pipette_dispense()
