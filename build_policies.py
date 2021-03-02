# Maybe where our policies are?

"""
PLEASE READ: When making a policy, use the SC2 keywords:
    train for units
    build for structures
    upgrade for abilities
as a preface to the keys (we'll have to agree on correct keywords.

i.e. upgrade_ling_speed', 'build_pool', 'train_lurkers', "supply_for_lair', etc

Also, try to kee it alphabatized.
"""
default = {
    'build_lair': True,
    'build_pool': True,
    'max_drones': 85,
    'max_overlords': 20,  # 200/their supply count
    'supply_for_lair': 35,
    'time_for_lair': 3.00,
    'upgrade_overlord_speed': True,
}

zerg_rush_6pool = {
    'build_pool': True,
    'build_order': [1, 2, 3, 4],
    'supply_for_pool': 6,  # when supply is 6
    'supply_for_lair': 30,
    'time_for_lair': 8.00,
    'train_ling_speed': True,
}

muta_bane_ling = {
    'supply_for_pool': 12,  # when supply is 6
    'build_order': [1, 2, 3, 4],
    'build_spire': True,
    'build_pool': True,
    'build_bane_nest': True,
    'max_lings': 100,
    'max_mutas': 15,
    'supply_for_second_expac': 22,
    'supply_for_lair': 30,
    'time_for_lair': 5.00,
    'train_ling': True,
    'train_muta': True,
    'upgrade_bane_speed': True,
}
