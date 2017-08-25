import pytest

from opentrons.trackers import position_tracker as pt
from opentrons.trackers import calibration_functions
from opentrons.trackers import position_tracker
from opentrons import containers
from opentrons.instruments import Pipette
from opentrons.containers import load as containers_load
from opentrons.util import trace



@pytest.fixture
def robot():
    from opentrons import Robot
    return Robot()

def test_pipette_aspirate(robot):
    p200 = Pipette(robot, 'a')
    assert p200 in robot.liquid_tracker
    






