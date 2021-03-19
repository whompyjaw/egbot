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

