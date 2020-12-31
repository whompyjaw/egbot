from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from units.drone import Drone


class MacroManager:

    macro_actions = []

    def __init__(self, bot, structures):
        self.bot = bot
        self.structures = structures
        self.hq = None
        # self.hq = structures.firstexpansion

    async def build_pool(self):  # Build spawning pool
        if (
            self.structures(UnitTypeId.SPAWNINGPOOL).amount
            + self.already_pending(UnitTypeId.SPAWNINGPOOL)
            == 0
        ):
            if self.can_afford(UnitTypeId.SPAWNINGPOOL):
                await self.build(
                    UnitTypeId.SPAWNINGPOOL,
                    near=hq.position.towards(self.game_info.map_center, 5),
                )

    async def build_gas(self):
        if self.can_afford(UnitTypeId.EXTRACTOR):
            # May crash if we dont have any drones
            for hatch in self.townhalls.ready:
                for vg in self.vespene_geyser.closer_than(10, hatch):
                    if not self.worker_en_route_to_build(UnitTypeId.EXTRACTOR):
                        await self.build(UnitTypeId.EXTRACTOR, vg)
                        break

    def add_structure(self, unit):
        self.structures = unit
