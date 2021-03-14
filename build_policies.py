# # Maybe where our policies are?
#
# """
# **PLEASE READ**
# When making a policy, use the SC2 keywords:
#     train for units
#     build for structures
#     upgrade for abilities
# as a preface to the keys (we'll have to agree on correct keywords.
#
# i.e. upgrade_ling_speed', 'build_pool', 'train_lurkers', "supply_for_lair', etc
#
# Also, try to kee it alphabatized.
# """
# from build_policy_consts import *
#
# default = {
#     BUILD_LAIR: True,
#     BUILD_HIVE: True,
#     BUILD_POOL: True,
#     MAX_DRONE: 85,
#     MAX_OVERLORD: 20,  # 200/their supply count
#     TRAIN_OVERSEER: True,
#     UPGRADE_OVERLORD_SPEED: True,
#
# }
#
# ling_hydra = {
#
# }
#
# roach_hydra = {
#     BUILD_HYDRADEN: True,
#     BUILD_ROACHWARREN: True,
#     MAX_ROACH: 50,
#     MAX_HYDRA: 50,
#     MAX_LING: 16,
#     TRAIN_ROACH: True,
#     TRAIN_RAVAGER: True,
#     TRAIN_HYDRA: True,
#     TIME_FOR_LAIR: 5.00,
#     SUPPLY_FOR_LAIR: 20,
# }
#
# zerg_rush_6pool = {
#     'build_pool': True,
#     'build_order': [1, 2, 3, 4],
#     'supply_for_pool': 6,  # when supply is 6
#     'supply_for_lair': 30,
#     'time_for_lair': 8.00,
#     'train_ling_speed': True,
# }
#
# muta_bane_ling = {
#     'supply_for_pool': 12,  # when supply is 6
#     'build_order': [1, 2, 3, 4],
#     'build_spire': True,
#     'build_pool': True,
#     'build_bane_nest': True,
#     'max_lings': 100,
#     'max_mutas': 15,
#     'supply_for_second_expac': 22,
#     'supply_for_lair': 30,
#     'time_for_lair': 5.00,
#     'train_ling': True,
#     'train_muta': True,
#     'upgrade_bane_speed': True,
# }
