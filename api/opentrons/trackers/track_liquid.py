from opentrons.util import trace
from opentrons.util import liquid_functions as lf


broker = trace.MessageBroker.get_instance()


DEFAULT_STATES = {}


class WellLiquidTracker(object):
    def __init__(self):
        self._well_dict = {}

    def __del__(self):
        pass
    def __getitem__(self, item):
       return self._well_dict[id(item)]

    def __setitem__(self, item, value):
        self._well_dict[id(item)] = value

    def register(self, well, liquid_contents={}):
        self[well] = liquid_contents



   def _liquid_state_handler(self, event_type, event_info):
        if event_type == 'dispense':
            self._state['liquids'], self._state['volume'] = \
                lf.add_liquids(self._state['liquids'],
                               self._state['volume'],
                               event_info['liquids'],
                               event_info['volume'])

    def add_liquid(self, well, liquid):
        pass