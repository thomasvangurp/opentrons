from opentrons.util.trace import MessageBroker
# from opentrons.util import liquid_functions as lf
from opentrons.pubsub_util.topics import LIQUID_TRANSFER
from opentrons.pubsub_util.messages.liquid import liquid_transfer_msg

message_broker = MessageBroker.get_instance()


def relative_proportions_to_percentages(liquid_dict):
    liquids_as_percent = {
        liquid: (proportion / sum(liquid_dict.values()))
        for liquid, proportion in liquid_dict.items()}
    return liquids_as_percent


def combine_liquids(liq1, liq2):
    '''
    combine two liquids together

    '''
    liq_by_vols_1, liq_by_vols_2 = [
        {liquid: (ratio * liq_holder.volume)
            for liquid, ratio in liq_holder.liquids.items()}
        for liq_holder in [liq1, liq2]]

    # combine dicts to account for the disjunctive union
    combined_liqs = {**liq_by_vols_1, **liq_by_vols_2}

    # adjust to combine the original volumes of liquids in the intersection
    for liquid in liq1.liquids.keys() & liq2.liquids.keys():
        combined_liqs.update({
            liquid: liq_by_vols_1[liquid] + liq_by_vols_2[liquid]})

    # Resolve volumes back to proportions
    total_volume = sum(combined_liqs.values())
    combined_liqs_ratios = {
        liquid: volume / total_volume
        for liquid, volume in combined_liqs.items()}
    return LiquidContent(combined_liqs_ratios, total_volume)


class LiquidContent(object):
    def __init__(self, liquid_dict, volume):
        self._liquids = relative_proportions_to_percentages(liquid_dict)
        self._volume = volume

    def __repr__(self):
        return "Liquid: {} \nVolume: {}".format(self._liquids, self._volume)

    def __eq__(self, other):
        return (self._liquids == other._liquids
                and self._volume == other._volume)

    def __add__(self, other):
        return combine_liquids(self, other)

    @property
    def liquids(self):
        return self._liquids

    @liquids.setter
    def liquids(self, liquid_dict):
        self._liquids = relative_proportions_to_percentages(liquid_dict)

    @property
    def volume(self):
        return self._volume

    @volume.setter
    def volume(self, vol):
        self._volume = vol


class LiquidTracker(object):
    def __init__(self, message_broker: MessageBroker):
        self._liquid_holder_dict = {}
        message_broker.subscribe(LIQUID_TRANSFER, self._liquid_transfer_event)

    def __contains__(self, item):
        return item in self._liquid_holder_dict

    def __iter__(self):
        return iter(self._liquid_holder_dict)

    def __setitem__(self, liq_holder, liquid_contents: LiquidContent):
        if not isinstance(liquid_contents, LiquidContent):
            raise TypeError("{} is not an instance of LiquidContent".format(liquid_contents))  # noqa: E501
        self._liquid_holder_dict[liq_holder] = liquid_contents

    def __repr__(self):
        return repr(self._liquid_holder_dict)

    def __del__(self):
        pass

    def __getitem__(self, item):
        return self._liquid_holder_dict[item]

    def _track_liquid_holder(self, liq_holder, liquid_contents: LiquidContent):
        self[liq_holder] = liquid_contents

    def track_liquid_holder(self, liq_holder, contents=None):
        if not contents:
            contents = LiquidContent({}, 0)
        self._track_liquid_holder(liq_holder, contents)

    def _extract_liquid(self, liq_holder, volume):
        self[liq_holder].volume -= volume
        return LiquidContent(self[liq_holder].liquids, volume)

    def _add_liquid(self, liq_holder, liquid_to_add):
        self[liq_holder] += liquid_to_add

    def transfer_liquid(self, src, dest, volume):
        '''
        Transfers liquid from one liq_holder to another
        '''
        liquid = self._extract_liquid(src, volume)
        self._add_liquid(dest, liquid)

    def _liquid_transfer_event(self, liquid_transfer: liquid_transfer_msg):
        '''
        liquid_movement_msg(
            source='source', destination='dest', liquid_contents={})
        '''
        # TODO: update this example with a real liq_transfer_msg
        src, dest, volume = liquid_transfer
        self.transfer_liquid(src, dest, volume)

    def add_liquid(self, liquid_holder, liquid_name, volume):
        liq_to_add = LiquidContent({liquid_name: 1}, volume)
        self._add_liquid(liquid_holder, liq_to_add)
