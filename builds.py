from sc2.unit import UnitTypeId as id
from constants import *


class DefaultBuild:
    def __init__(self, bot):
        self.bot = bot
        self.units_to_train = {}
        self.build_sequence = []
        self.build_lair = True
        self.build_hive = True
        self.build_evo_chamber = True
        # might be better to create a list of structures we will have in general, but not necessarily sequential


class LingHydra(DefaultBuild):
    def __init__(self, bot):
        super().__init__(bot)
        self.build_sequence = [id.SPAWNINGPOOL, id.LAIR, id.HYDRALISKDEN]
        self.units_to_train = {
            id.DRONE: {
                # drone doesn't really have a structure requirement
                STRUCTURE: id.HATCHERY,
                WEIGHT: .425,
                SUPPLY_COST: 1
            },
            id.QUEEN: {
                STRUCTURE: id.SPAWNINGPOOL,
                WEIGHT: .04,
                SUPPLY_COST: 2
            },
            id.ZERGLING: {
                STRUCTURE: id.SPAWNINGPOOL,
                WEIGHT: .185,
                SUPPLY_COST: 1
            },
            id.HYDRALISK: {
                STRUCTURE: id.HYDRALISKDEN,
                WEIGHT: .35,
                SUPPLY_COST: 2
            }
        }
        # i don't think i need to add things for evo chambers
