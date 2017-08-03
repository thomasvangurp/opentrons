import unittest

from opentrons import robot
from opentrons.containers import load as containers_load
from opentrons.instruments import pipette
from pytest import approx
# from opentrons.tracker import Tracker


# def test_adding_to_dict_on_load():
#     trash = containers_load(robot, 'point', 'A1')
#     assert trash.state == {'liquid_volume': 0, 'liquid_height': 0}


# def test_liquid_tracking():
#     robot = Robot()

#     trash = containers_load(robot, 'point', 'A1')

#     tiprack1 = containers_load(robot, 'tiprack-10ul', 'B2')
#     plate = containers_load(robot, '96-flat', 'A2')

#     p200 = pipette.Pipette(
#         robot,
#         axis="b",
#         trash_container=trash,
#         tip_racks=[tiprack1],
#         max_volume=200,
#         min_volume=10,  # These are variable
#         channels=1,
#         name='other-pipette-for-transfer-tests'
#     )

#     plate['A1'].add_volume(5000)

#     p200.pick_up_tip()
#     p200.aspirate(plate['A1'])
#     p200.dispense(plate['A2'])

#     assert plate['A2'].volume == 200
#     assert plate['A1'].volume == 4800


def test_liquid_tracking():
    from opentrons.tracker import Tracker

    trash = containers_load(robot, 'point', 'A1')
    tiprack1 = containers_load(robot, 'tiprack-10ul', 'B2')
    plate = containers_load(robot, '96-flat', 'A2')

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

    wells = {
        well: {'red': 30, 'green': 30, 'blue': 30}
        for well in plate.wells()}

    tracker = Tracker(instruments=[p200], state=wells)

    p200.aspirate(30, plate['A1'])
    p200.dispense(30, plate['A2'])

    # Using approx to compare floating point numbers
    # More here: https://docs.pytest.org/en/latest/builtin.html#comparing-floating-point-numbers  # NOQA
    assert plate['A1'].volume == approx(60)
    assert plate['A2'].volume == approx(120)
    assert plate['A1'].liquids == approx({'red': 20, 'green': 20, 'blue': 20})
    assert plate['A2'].liquids == approx({'red': 40, 'green': 40, 'blue': 40})
