import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.ids.unit_typeid import UnitTypeId
from sc2.player import Bot, Computer
from sc2.unit import Unit
from sc2.units import Units
import logging
import random
import itertools

from managers.macro import MacroManager
from managers.unit import UnitManager

# importing from other folders
# from folder.folder.file import Whatever

logging.basicConfig(
    level=logging.DEBUG,
    filename="egbot.log",
    datefmt="%d-%m-%y %H:%M:%S",
    format="%(asctime)s | %(levelname)s | %(funcName)s | ln:%(lineno)d | %(message)s",
)


class EGbot(sc2.BotAI):
    def __init__(self):
        self.mm = MacroManager(self)
        self.um = UnitManager(self)
        self.iteration = 0

    async def on_step(self, iteration):
        self.iteration = iteration
        self.um.update_units()
        await self.mm.build_drone(self.um.units, self.um.drone, self.um.overlord)
        await self.mm.build_overlords(self.um.units, self.um.overlord)
        await self.mm.build_pool()
        await self.mm.build_gas()
        await self.mm.expand()
        await self.mm.build_queens(self.um.units)
        await self.um.do_queen_injects()
        await self.distribute_workers(1.0)
        # await self.spread_creep()
    
    async def on_before_start(self):
        mfs = self.mineral_field.closer_than(10, self.townhalls.random)
        for drone in self.units(UnitTypeId.DRONE):
            drone.gather(mfs.closest_to(drone))

    async def on_building_construction_complete(self, unit: Unit):
        """ Set rally point of new hatcheries. """
        if unit.type_id == UnitTypeId.HATCHERY:
            self.mm.update_townhalls()
            if self.mineral_field:
                mf = self.mineral_field.closest_to(unit)
                unit.smart(mf)
        self.mm.add_structure(unit)

    async def on_unit_created(self, unit):
        self.um.add_unit(unit)

    async def on_unit_destroyed(self, unit_tag: int):  
        await self._remove_unit(unit_tag)

    async def on_unit_type_changed(self, unit: Unit, previous_type: UnitTypeId):
        pass

    async def _remove_unit(self, tag: int):
        units = self.um.units
        structures = self.mm.structures

        for unit_type in list(units.keys()):
            if tag in units[unit_type].keys():
                units[unit_type].pop(tag)
                break

        for struct_type in list(structures.keys()):
            if tag in structures[struct_type].keys():
                structures[struct_type].pop(tag)
                break

"""Setting realtime=False makes the game/bot play as fast as possible"""
run_game(maps.get("AbyssalReefLE"), [Bot(Race.Zerg, EGbot()), Computer(Race.Terran, Difficulty.Easy)], realtime=False)
