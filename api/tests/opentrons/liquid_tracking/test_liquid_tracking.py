import unittest

from opentrons import robot
from opentrons.containers import load as containers_load
from opentrons.instruments import pipette
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
        well.get_name(): {'red': 100, 'green': 100, 'blue': 100}
        for well in plate.wells()}

    tracker = Tracker({p200.name: {}, **wells})

    p200.aspirate(100, plate['A1'])
    p200.dispense(100, plate['A2'])

    assert wells[plate['A1']] == {'red': 66, 'green': 66, 'blue': 66}
    assert wells[plate['A2']] == {'red': 133, 'green': 133, 'blue': 133}
