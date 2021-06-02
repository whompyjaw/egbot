from sc2.unit import UnitTypeId as id
from constants import *


class DefaultBuild:
    def __init__(self, bot):
        self.bot = bot
        self.units_to_train = {}
        self.build_sequence = {
            id.HATCHERY: {
                HATCH_1: {SUPPLY_REQ: 16, TOWNHALL_REQUIREMENT: 2},
                HATCH_2: {SUPPLY_REQ: 30, TOWNHALL_REQUIREMENT: 3},
                HATCH_3: {SUPPLY_REQ: 76, TOWNHALL_REQUIREMENT: 4},
                HATCH_4: {SUPPLY_REQ: 108, TOWNHALL_REQUIREMENT: 5},
            },
            id.EXTRACTOR: {
                EXTRACTOR_1: {SUPPLY_REQ: 18, EXTRACTOR_COUNT: 1},
                EXTRACTOR_2: {SUPPLY_REQ: 40, EXTRACTOR_COUNT: 2},
                EXTRACTOR_3: {SUPPLY_REQ: 64, EXTRACTOR_COUNT: 3},
                EXTRACTOR_4: {SUPPLY_REQ: 78, EXTRACTOR_COUNT: 4},
            },
            id.EVOLUTIONCHAMBER: {
                EVO_1: {SUPPLY_REQ: 32, EVO_COUNT: 1},
                EVO_2: {SUPPLY_REQ: 34, EVO_COUNT: 2},
            },
            id.SPAWNINGPOOL: {
                LOCATION:  self.bot.townhalls.ready.random.position.towards(self.bot.game_info.map_center, 5),
                SUPPLY_REQ: 17,
                BEFORE_HATCH: False,
            },
            id.LAIR: {
                LOCATION: self.bot.gm.macromgr.hq.position,
                SUPPLY_REQ: 42,
            },
        }
        self.units_to_train = {
            id.DRONE: {
                # drone doesn't really have a structure requirement
                STRUCTURE_REQ: id.HATCHERY,
                WEIGHT: 0.425,
                SUPPLY_COST: 1
            },
            id.QUEEN: {
                STRUCTURE_REQ: id.SPAWNINGPOOL,
                WEIGHT: 0.04,
                SUPPLY_COST: 2
            },
            id.ZERGLING: {
                STRUCTURE_REQ: id.SPAWNINGPOOL,
                WEIGHT: .185,
                SUPPLY_COST: 0.5
            },
        }
        self.build_lair = True
        self.build_hive = True
        self.build_evo_chamber = True
        self.expand_rate = 16 # TODO: Do we need this?
        # might be better to create a list of structures we will have in general, but not necessarily sequential


class LingHydra(DefaultBuild):
    def __init__(self, bot):
        super().__init__(bot)
        self.build_sequence.update({
            id.LAIR: {
                LOCATION: self.bot.gm.macromgr.hq.position,
                SUPPLY_REQ: 42,
            },
            id.HYDRALISKDEN: {
                LOCATION: self.bot.gm.macromgr.hq.position.towards_with_random_angle(self.bot.game_info.map_center, 10),
                SUPPLY_REQ: 56,
            }
        })
        self.units_to_train = {
            id.DRONE: {
                # drone doesn't really have a structure requirement
                STRUCTURE_REQ: id.HATCHERY,
                WEIGHT: 0.425,
                SUPPLY_COST: 1
            },
            id.QUEEN: {
                STRUCTURE_REQ: id.SPAWNINGPOOL,
                WEIGHT: 0.04,
                SUPPLY_COST: 2
            },
            id.ZERGLING: {
                STRUCTURE_REQ: id.SPAWNINGPOOL,
                WEIGHT: 0.185,
                SUPPLY_COST: 1
            },
            id.HYDRALISK: {
                STRUCTURE_REQ: id.HYDRALISKDEN,
                WEIGHT: 0.35,
                SUPPLY_COST: 2
            }
        }

class LingBaneMuta(DefaultBuild):
    def __init__(self, bot):
        super().__init__(bot)
        self.build_sequence.update({
            id.EXTRACTOR: {
                EXTRACTOR_1: {SUPPLY_REQ: 18, EXTRACTOR_COUNT: 1},
                EXTRACTOR_2: {SUPPLY_REQ: 24, EXTRACTOR_COUNT: 2},
                EXTRACTOR_3: {SUPPLY_REQ: 42, EXTRACTOR_COUNT: 3},
                EXTRACTOR_4: {SUPPLY_REQ: 46, EXTRACTOR_COUNT: 4},
            },
            id.LAIR: {
                LOCATION: self.bot.gm.macromgr.hq.position,
                SUPPLY_REQ: 42,  # TODO: Might need to customize this value to better fit Muta timing
            },
            id.BANELINGNEST: {
                LOCATION: self.bot.gm.macromgr.hq.position.towards_with_random_angle(self.bot.game_info.map_center, 10),
                SUPPLY_REQ: 23,
            },
            id.SPIRE: {
                LOCATION: self.bot.townhalls.random.position.towards_with_random_angle(self.bot.game_info.map_center, 7),
                SUPPLY_REQ: 56
            }
        })
        self.units_to_train.update({
            id.ZERGLING: {
                STRUCTURE_REQ: id.SPAWNINGPOOL,
                WEIGHT: 0.235,
                SUPPLY_COST: 1
            },
            id.BANELING: {
                STRUCTURE_REQ: id.BANELINGNEST,
                WEIGHT: 0.05,
                SUPPLY_COST: 0.5,
                MORPH_RATE: 5,
                UNIT_REQ: id.ZERGLING,
                MORPH_DISTR_REQ: 0.60  # note i don't know if this should go here or in the attributes of the req'd unit.
            },
            id.MUTALISK: {
                STRUCTURE_REQ: id.SPIRE,
                WEIGHT: 0.20,
                SUPPLY_COST: 2
            }
        })
