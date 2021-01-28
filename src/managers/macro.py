from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units
from collections import defaultdict
from structures import NewStructure, Hatchery, Extractor, SpawningPool
import constants
import dictops


class MacroManager:

    macro_actions = []

    def __init__(self, bot):
        self.bot = bot
        self.hq = None
        self.structures = defaultdict(dict)
        self.all_hatches = None
        self.rdy_hatches = None
        self.num_rdy_hatches = None
        self.inject_interval = 100

    def add_structure(self, structure: Unit):
        """
        Adds a new structure to self.structures.  Called in on_building_construction_completed
        
        :params Unit:
        """
        if structure.name == 'Hatchery':
            new_struct = Hatchery(structure)

        if structure.name == 'SpawningPool':
            new_struct = SpawningPool(structure)

        if structure.name == 'Extractor':
            new_struct = Extractor(structure)

        self.structures[new_struct.name][new_struct.tag] = new_struct


    async def build_pool(self):
        """Builds a Spawning Pool near starting Hatchery location"""
        if self.structures.get('SpawningPool') == None:
            if not self.bot.already_pending(UnitTypeId.SPAWNINGPOOL):
                if self.bot.can_afford(UnitTypeId.SPAWNINGPOOL):
                    await self.bot.build(
                        UnitTypeId.SPAWNINGPOOL,
                        near=self.hq.position.towards(self.bot.game_info.map_center, 5),
                    )

    async def build_gas(self):
        """
        Build Extractors at Vespene Gas locations near Hatchery. If only one
        hatch is up, build one gas, once hatches.amount > 1 then begin building gas at all locations. 
        """
        hatch_count = dictops.get_count(self.structures, 'Hatchery')

        if hatch_count == 1 and self.bot.already_pending(UnitTypeId.SPAWNINGPOOL):
            if self.bot.can_afford(UnitTypeId.EXTRACTOR) and not self.bot.already_pending(UnitTypeId.EXTRACTOR):
                if self.structures.get('Extractor') == None:
                    for vg in self.bot.vespene_geyser.closer_than(10, self.hq):
                        await self.bot.build(UnitTypeId.EXTRACTOR, vg)
                        break

        elif hatch_count > 1:            
            if self.bot.can_afford(UnitTypeId.EXTRACTOR):
                for hatch in self.all_hatches:
                    for vg in self.bot.vespene_geyser.closer_than(10, hatch):
                        if not self.bot.worker_en_route_to_build(UnitTypeId.EXTRACTOR):
                            await self.bot.build(UnitTypeId.EXTRACTOR, vg)
                            break

    async def expand(self):
        """
        Expands to nearest location when 300 minerals are available up to maximum 5 hatcheries
        Currently this doesn't account for if enemies are in the way I guess (per a note from the sc2 lib)
        """
        hatch_count = dictops.get_count(self.structures, 'Hatchery')

        if (hatch_count + self.bot.already_pending(UnitTypeId.HATCHERY)) < 5:
            if self.bot.can_afford(UnitTypeId.HATCHERY):
                next_expac = await self.bot.get_next_expansion()
                # select drone
                # TODO: Try to select drone that is pending or is in egg form (for strategy sprint)
                worker = self.bot.select_build_worker(next_expac)
                if worker:
                    worker.build(UnitTypeId.HATCHERY, next_expac)
                
    
    async def build_drone(self, units: {}, drone: UnitTypeId, overlord: UnitTypeId):
        """
        Builds drones; drone limit based on # of hatcheries; 22 drones per hatchery 
        """
        larvae = Units(dictops.get_values(units, 'Larva'), self.bot)
        if (larvae and self.bot.can_afford(drone)
            and (self.bot.supply_left > 1 or self.bot.already_pending(overlord))>= 1):
            if (
                self.bot.supply_workers
                - self.bot.worker_en_route_to_build(UnitTypeId.HATCHERY)
                + self.bot.already_pending(drone)
            ) < 85:
                larvae.random.unit.train(drone)

    async def build_overlords(self, units: {}, overlord: UnitTypeId):
        """
        TODO: Will need to figure out if we need to create more than 200 supply OLs
        """
        larvae = Units(dictops.get_values(units, 'Larva'), self.bot)
        if self.bot.supply_used <= 13 and self.bot.already_pending(overlord) < 1:
            larvae.random.unit.train(overlord)
        elif (
            self.bot.supply_cap > 14
            and self.bot.supply_left < 2
            and larvae
            and self.bot.can_afford(overlord)
            and self.bot.already_pending(overlord) < 2
        ):
            larvae.random.unit.train(overlord)

    def update_townhalls(self):
        self.hq = self.bot.townhalls.first
        self.all_hatches = self.bot.townhalls
        self.rdy_hatches = self.bot.townhalls.ready
        self.num_rdy_hatches = self.bot.townhalls.ready.amount

    async def build_queens(self, units: {}):
        """
        If a pool exists and bot can afford build a queen.

        :params: list of Queens
        """
        queen_count = dictops.get_count(units, 'Queen')
        hatches = dictops.get_values(self.structures, 'Hatchery')
        if (
            self.structures.get('SpawningPool') != None and (queen_count <= (self.num_rdy_hatches + 2))
            and self.bot.already_pending(UnitTypeId.QUEEN) < 1
        ):
            if self.bot.can_afford(UnitTypeId.QUEEN):
                for hatchery in hatches:
                    if hatchery.unit.is_idle:
                        hatchery.unit.train(UnitTypeId.QUEEN)

