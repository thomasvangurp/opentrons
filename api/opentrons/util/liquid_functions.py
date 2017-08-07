import math





#TODO: Need to decide on contamination tracking. Should a pipette with now 0 volume,
# but that has not been reset discard its previous contents? Maybe it should only
# reset on new a tip? Maybe it should be marked as dirty?
#
def add_liquids(src_liq_dict, src_vol, dest_liq_dict, dest_vol):
    '''
    add two liquids together

    Takes in a dictionary of liquid names and their
    relative proportions for both source and destination
    as well as the volume of each.

    Returns a dict of the new relative proportions and the total volume

    :param src_liq_dict:
    :param src_vol:
    :param dest_liq_dict:
    :param dest_vol:
    :return:
    '''

    #if their is no destination liquid
    # then it now contains the source liquid
    if dest_vol == 0:
        return (src_liq_dict, src_vol)
    if src_vol == 0:
        return (dest_liq_dict, dest_vol)

    # convert proportions to volumes
    src_liq_vols = {k: v/sum(src_liq_dict.values()) *
                       src_vol for k, v in src_liq_dict.items()}
    dest_liq_vols = {k: v/sum(dest_liq_dict.values()) *
                        dest_vol for k, v in dest_liq_dict.items()}

    # combine dicts to account for the disjunctive union
    combined_liqs = {**src_liq_vols, **dest_liq_vols}

    # adjust to combine the original volumes of liquids in the intersection
    for liquid_key in src_liq_dict.keys() & dest_liq_dict.keys():
        combined_liqs.update({liquid_key: dest_liq_vols[liquid_key] + src_liq_vols[liquid_key]})

    # Resolve volumes back to proportions
    total_volume = sum(combined_liqs.values())
    combined_liqs_ratios = {k: v/total_volume for k, v in combined_liqs.items()}
    return (combined_liqs_ratios, total_volume)


def well_liquid_height(well):
    vol = well.volume
    radius = well.properties['diameter']/2
    height = vol / (math.pi *  math.pow(radius, 2))
    return height



