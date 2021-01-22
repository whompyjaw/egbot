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
        # self.hatch_strat = random.randint(1, 3)
        self.mm = MacroManager(self)
        self.um = UnitManager(self)
        self.iteration = 0

    async def on_step(self, iteration):
        self.iteration = iteration
        self.um.update_units()
        # Send workers across bases
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
               # sets gathering location to mineral patch near recently built hatch
          #logging.debug(f"{unit.name} has completed.")
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
        for unit_type in units.keys():
            for unit_tag in units[unit_type].keys():
                if unit_tag == tag: 
                    units[unit_type].pop(tag)
                    break
                

        # for struct_type in structures.keys():   
        #     structures[struct_type].pop(tag)
        #     break
        '''TODO Error: dictionary changed size during iteration.  I think it has
        something to do with the cacoons that spawn drones, etc.  when they are destroyed
        the dictionary changes size? but at the same time, a Queen: {} is added in the beginning
        and I can't find the code that causes that...'''
        for struct_type in structures.keys():
            for struct_tag in structures[unit_type].keys():
                if struct_tag == tag:   
                    structures[struct_type].pop(tag)
                    break  


"""Setting realtime=False makes the game/bot play as fast as possible"""
run_game(maps.get("AbyssalReefLE"), [Bot(Race.Zerg, EGbot()), Computer(Race.Terran, Difficulty.Easy)], realtime=False)
