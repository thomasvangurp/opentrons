import copy

from opentrons.util import trace
from opentrons import containers
from opentrons.containers import WellSeries


def ensure_keys(state, path):
    parent = state
    for p in path:
        if p not in parent:
            parent[p] = {}
        parent = parent[p]
    return state


def total_volume(state):
    return sum(state.values())


def concentrations(state):
    # if any of our children is a dict, go one level deeper
    # alternatively we can test if each is not a number
    if any((isinstance(value, dict) for value in state.values())):
        return {
            key: concentrations(value)
            for key, value in state.items()
        }

    t = total_volume(state)
    return {
        key: value / t if t else 0  # if volume is 0, concentration is 0
        for key, value in state.items()
    }


def substract(state, volume):
    d = volume / total_volume(state)
    new_state = {
        key: value * (1.0 - d)
        for key, value in state.items()
    }

    volume = {
        key: value - new_state[key]
        for key, value in state.items()
    }

    return new_state, volume


def add(state_1, state_2):
    res = {
        key: state_1.get(key, 0.0) + state_2.get(key, 0.0)
        for key in set(state_1) | set(state_2)
    }
    return res


def aspirate(state, volume, instrument, source):
    state = ensure_keys(state, [instrument])

    # if aspirating from non-existent container/well
    # we'll make it known by marking a transfer volume
    volume_dict = {
        'unknown-from-{}'.format(source): volume
    }

    if not isinstance(source, WellSeries):
        source = [source]
    for s in source:
        if s in state:
            new_state, volume_dict = substract(state[s], volume)
            state[s] = new_state

    state[instrument] = add(volume_dict, state[instrument])
    return state


def dispense(state, volume, instrument, destination):
    if not isinstance(destination, WellSeries):
        destination = [destination]
    for d in destination:
        state = ensure_keys(state, [d])

    new_state, volume = substract(state[instrument], volume)
    state[instrument] = new_state

    for d in destination:
        state[d] = add(volume, state[d])
    return state


class Tracker(object):
    # Map names of functions to state transformation actions
    event_mapping = {
        'Pipette.dispense': dispense,
        'Pipette.aspirate': aspirate
    }

    def update_volume_attributes(self, item):
        # No liquid yet. Nothing to do.
        if item not in self.state:
            return

        setattr(item, 'liquids', self.state[item])
        setattr(item, 'volume', sum(self.state[item].values()))
        setattr(item, 'concentrations', concentrations(self.state[item]))

    def __init__(self, instruments, state):
        self.state = state
        self.instruments = instruments
        [self.update_volume_attributes(item) for item in state.keys()]
        trace.EventBroker.get_instance().add(self.handler)

    def handler(self, info):
        if 'function' not in info:
            return

        arguments = info['arguments']
        function = info['function']

        if function not in Tracker.event_mapping:
            return

        if arguments['self'] not in self.instruments:
            return

        action = Tracker.event_mapping[function]
        well = arguments['location']

        self.state = action(
            self.state,
            arguments['volume'],
            arguments['self'],
            well)

        self.update_volume_attributes(well)

    def init(self, state=None):
        if not state:
            state = {}
        self.initial_state = state
        reset()

    def reset(self):
        self.state = {}
        for k, v in self.initial_state.items():
            self.state[k] = v
