from opentrons.util import trace
from opentrons.containers.placeable import WellSeries
from opentrons import containers


_tracker_state = {}
_tracker_init_state = {}


def liquid_event(data):
    global _tracker_state
    name = data.get('name')

    if name is not 'aspirate' and name is not 'dispense':
        return

    location = data.get('location')
    volume = data.get('volume')
    pipette_axis = data.get('pipette')
    placeable, _ = containers.unpack_location(location)
    if isinstance(placeable, WellSeries):
        # TODO: alter volumes of each well in WellSeries
        pass

    if name is 'aspirate':
        _tracker_state = aspirate(
            _tracker_state, volume, pipette_axis, placeable)
    else:
        _tracker_state = dispense(
            _tracker_state, volume, pipette_axis, placeable)


trace.EventBroker.get_instance().add(liquid_event)


def init(state=None):
    global _tracker_init_state, _tracker_state
    if not state:
        state = {}
    _tracker_init_state = state
    reset()


def reset():
    global _tracker_init_state, _tracker_state
    _tracker_state = _tracker_init_state


def state():
    global _tracker_state
    return _tracker_state


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
        key: value / t
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

    if source in state:
        new_state, volume_dict = substract(state[source], volume)
        state[source] = new_state

    state[instrument] = add(volume_dict, state[instrument])
    return state


def dispense(state, volume, instrument, destination):
    state = ensure_keys(state, [destination])

    new_state, volume = substract(state[instrument], volume)
    state[instrument] = new_state
    state[destination] = add(volume, state[destination])
    return state
