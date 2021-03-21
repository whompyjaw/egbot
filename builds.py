from sc2.unit import UnitTypeId as id
from constants import *


class DefaultBuild:
    def __init__(self, bot):
        self.bot = bot
        self.units_to_train = {}
        self.build_sequence = {
            # id.SPAWNINGPOOL: {
            #     LOCATION: self.bot.gm.mm.hq.position.towards(self.bot.game_info.map_center, 5),
            #     SUPPLY: 17,
            # },
            # id.LAIR: {
            #     LOCATION: self.bot.gm.mm.hq.position,
            #     SUPPLY: 36,
            # },
            # id.HYDRALISKDEN: {
            #     LOCATION: self.bot.gm.mm.hq.position.towards(self.bot.game_info.map_center, 10),
            #     SUPPLY: 48,
            # }
        }
        self.build_lair = True
        self.build_hive = True
        self.build_evo_chamber = True
        self.expand_rate = 16
        # might be better to create a list of structures we will have in general, but not necessarily sequential



class LingHydra(DefaultBuild):
    def __init__(self, bot):
        super().__init__(bot)
        self.build_sequence = {
            id.HATCHERY: {
                HATCH_1: {SUPPLY: 16, TOWNHALL_REQUIREMENT: 2},
                HATCH_2: {SUPPLY: 30, TOWNHALL_REQUIREMENT: 3},
                HATCH_3: {SUPPLY: 64, TOWNHALL_REQUIREMENT: 4},
                HATCH_4: {SUPPLY: 90, TOWNHALL_REQUIREMENT: 5},
            },
            id.EXTRACTOR: {
                EXTRACTOR_1: {SUPPLY: 18, EXTRACTOR_COUNT: 1},
                EXTRACTOR_2: {SUPPLY: 40, EXTRACTOR_COUNT: 2},
                EXTRACTOR_3: {SUPPLY: 64, EXTRACTOR_COUNT: 3},
                EXTRACTOR_4: {SUPPLY: 78, EXTRACTOR_COUNT: 4},
            },
            id.SPAWNINGPOOL: {
                LOCATION: self.bot.gm.mm.hq.position.towards(self.bot.game_info.map_center, 5),
                SUPPLY: 17,
                BEFORE_HATCH: False,
            },
            id.LAIR: {
                LOCATION: self.bot.gm.mm.hq.position,
                SUPPLY: 42,
            },
            id.HYDRALISKDEN: {
                LOCATION: self.bot.gm.mm.hq.position.towards(self.bot.game_info.map_center, 10),
                SUPPLY: 56,
                    #self.bot.main_base_ramp.bottom_center.towards(self.bot.game_info.map_center, 3)
            }
        }
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

        # struct_dict = [{id.HATCHERY:{'location': await self.bot.get_next_expansion()},
        #                 id.SPAWNINGPOOL:{'location': self.hq.position.towards(self.bot.game_info.map_center, 5)},
        #                 id.EXTRACTOR:{'location': self.bot.vespene_geyser.closer_than(10, self.bot.townhalls.ready.random)},
        #                 id.HATCHERY:{'location': await self.bot.get_next_expansion()},
        #                 id.EXTRACTOR:{'location': self.bot.vespene_geyser.closer_than(10, self.bot.townhalls.ready.random)},
        #                 id.EVOLUTIONCHAMBER:{'location':self.bot.townhalls[1].position.towards(self.bot.game_info.map_center, 5)},
        #                 id.EVOLUTIONCHAMBER:{'location':self.bot.townhalls[1].position.towards(self.bot.game_info.map_center, 5)},
        #                 id.LAIR:{'location':self.bot.townhalls.first},
        #                 id.HYDRALISKDEN:{'location': self.bot.main_base_ramp.bottom_center.towards(self.bot.game_info.map_center, 3)}
        #                 }]
        #
        # async def build_stuff(self, structures: list):
        #     for struct in structures:
        #         #struct.keys() should return the UnitTypeId
        #         #struct.get('location') should return the build location
        #         #we then check if can afford
        #         self.bot.build(struct.keys(), struct.get('location'), can_afford_check=True)
        #         structures.pop(struct)
        #         break

