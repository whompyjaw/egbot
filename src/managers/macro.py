from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units
from dicts import NestedDefaultDict
from structures import SpawningPool, Hatchery, Extractor


class MacroManager:

    macro_actions = []

    def __init__(self, bot):
        self.bot = bot
        self.hq = None
        self.structures = NestedDefaultDict()
        self.all_hatches = None
        self.rdy_hatches = None
        self.num_rdy_hatches = None
        # self.hatch_name = ("Hatchery" or "Hive" or "Lair") 
        # self.used_tumors: Set[int] = set()
        self.inject_interval = 100

    def get_structure_count(self, struct_name: str):
        # TODO: We don't need this. len() would work if we ever need the count of something
        """Iterates through self.structures, returns int of specific structure name"""
        return [n for n in self.structures[struct_name].keys()]
    

    def add_structure(self, structure: Unit):
        """
        Adds a new structure to self.structures.  Called in on_building_construction_completed
        
        :params Unit:
        """
        #Hatchery
        if structure.name == 'Hatchery':
            new_struct = Hatchery(structure)
        #Spawning Pool
        if structure.name == 'SpawningPool':
            new_struct = SpawningPool(structure)
        #Extractor
        if structure.name == 'Extractor':
            new_struct = Extractor(structure)

        self.structures[new_struct.name][new_struct.tag] = new_struct


    async def build_pool(self):
        """Builds a Spawning Pool near starting Hatchery location"""
        # if not self.structures.get('SpawningPool'):
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
        if self.num_rdy_hatches == 1 and self.bot.already_pending(UnitTypeId.SPAWNINGPOOL):
            if self.bot.can_afford(UnitTypeId.EXTRACTOR) and not self.bot.already_pending(UnitTypeId.EXTRACTOR):
                if not self.structures['Extractor']:
                    for vg in self.bot.vespene_geyser.closer_than(10, self.hq):
                        await self.bot.build(UnitTypeId.EXTRACTOR, vg)
                        break

        elif self.num_rdy_hatches > 1:            
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
        if (self.num_rdy_hatches
            + self.bot.already_pending(UnitTypeId.HATCHERY)
            < 5
        ):
            if self.bot.can_afford(UnitTypeId.HATCHERY):
                next_expac = await self.bot.get_next_expansion()
                # select drone
                # TODO: Try to select drone that is pending or is in egg form
                worker = self.bot.select_build_worker(next_expac)
                if worker:
                    worker.build(UnitTypeId.HATCHERY, next_expac)
                
    
    async def build_drone(self, units: {}, drone: UnitTypeId, overlord: UnitTypeId):
        """
        Builds drones; drone limit based on # of hatcheries; 22 drones per hatchery 
        """
        larvae = Units(units['Larva'].values(), self.bot)
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
        larvae = Units(units['Larva'].values(), self.bot)
        # works with build_drones, ensures at game opening, only one OL is pending
        if self.bot.supply_used <= 13 and self.bot.already_pending(overlord) < 1:
            larvae.random.unit.train(overlord)
        # after we're above 13 supply, complete the normal OL method
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
        queens = units['Queen'].values()
        if (
            self.structures.get('SpawningPool') != None and (len(queens) <= (self.num_rdy_hatches + 2))
            and self.bot.already_pending(UnitTypeId.QUEEN) < 1
        ):
            if self.bot.can_afford(UnitTypeId.QUEEN):
                for hatchery in self.rdy_hatches:
                    if hatchery.is_idle:
                        hatchery.train(UnitTypeId.QUEEN)

