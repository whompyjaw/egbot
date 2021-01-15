from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units


class MacroManager:

    macro_actions = []

    def __init__(self, bot):
        self.bot = bot
        self.hq = None
        self.structures = []
        self.pool_name = "SpawningPool"
        self.all_hatches = None
        self.rdy_hatches = None
        self.num_rdy_hatches = None
        self.extractor_name = "Extractor"
        # self.hatch_name = ("Hatchery" or "Hive" or "Lair") 
        # self.used_tumors: Set[int] = set()
        self.inject_interval = 100

    def get_structure_count(self, struct_name: str):
        """Iterates through self.structures, returns int of specific structure name"""
        y = [x for x in self.structures if x.name == struct_name]
        return y

    def add_structure(self, structure: Unit):
        """
        Adds a new structure to self.structures.  Called in on_building_construction_completed
        
        :params Unit:
        """
        self.structures.append(structure)

    async def build_pool(self):
        """Builds a Spawning Pool near starting Hatchery location"""
        if not len(self.get_structure_count(self.pool_name)) == 1: 
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
        extractors = len(self.get_structure_count(self.extractor_name))
        if self.n_rdy_hatches == 1 and self.bot.already_pending(UnitTypeId.SPAWNINGPOOL):
            if self.bot.can_afford(UnitTypeId.EXTRACTOR) and not self.bot.already_pending(UnitTypeId.EXTRACTOR):
                if extractors == 0:
                    for vg in self.bot.vespene_geyser.closer_than(10, self.hq):
                        await self.bot.build(UnitTypeId.EXTRACTOR, vg)
                        break

        elif self.n_rdy_hatches > 1:            
            if self.bot.can_afford(UnitTypeId.EXTRACTOR):
                for hatch in self.n_hatches:
                    for vg in self.bot.vespene_geyser.closer_than(10, hatch):
                        if not self.bot.worker_en_route_to_build(UnitTypeId.EXTRACTOR):
                            await self.bot.build(UnitTypeId.EXTRACTOR, vg)
                            break

    async def expand(self):
        """
        Expands to nearest location when 300 minerals are available up to maximum 5 hatcheries
        1. get list of all expansions
        2. get enemy expansion location
          a. enemy_start_locations
          b. 
        3. select a drone that is pending > idle > mineral line
          a. select_bulid_worker
        4. check if can afford
        5. check if enemy is in location
          a. can_place
          b. find_placement
          c. in_pathing_grid? also in_placement_grid
        possible_expax = self.bot.expansion_locations()
        get list of enemy expansions
         """
        # get list of all expansions
        # possible_expansions = self.bot.expansion_locations_list
        # owned_expansions = self.bot.owned_expansions()
        # enemy_expansions = self.bot.enemy_start_locations()
        # get_next_expansion() will be of use

        """
        Currently this doesn't account for if enemies are in the way I guess (per a note from the sc2 lib)
        """
        if (self.n_rdy_hatches
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
                
    
    async def build_drone(self, larvae: UnitTypeId, drone: UnitTypeId, overlord: UnitTypeId):
        """
        Builds drones; drone limit based on # of hatcheries; 22 drones per hatchery 
        TODO: Need to change for late game to limit drone production when > 4 hatcheries
        TODO: Change 'en_route_to_build' to include all buildings
        """
        if (larvae and self.bot.can_afford(drone)
            and (self.bot.supply_left > 1 or self.bot.already_pending(overlord))>= 1):
            if (
                self.bot.supply_workers
                - self.bot.worker_en_route_to_build(UnitTypeId.HATCHERY)
                + self.bot.already_pending(drone)
            ) < 85:
                larvae.random.train(drone)

    async def build_overlords(self, larvae: UnitTypeId, overlord: UnitTypeId):
        """
        TODO: Will need to figure out if we need to create more than 200 supply OLs
        """
        # works with build_drones, ensures at game opening, only one OL is pending
        if self.bot.supply_used <= 13 and self.bot.already_pending(overlord) < 1:
            larvae.random.train(overlord)
        # after we're above 13 supply, complete the normal OL method
        elif (
            self.bot.supply_cap > 14
            and self.bot.supply_left < 2
            and larvae
            and self.bot.can_afford(overlord)
            and self.bot.already_pending(overlord) < 2
        ):
            larvae.random.train(overlord)

    def update_townhalls(self):
        self.hq = self.bot.townhalls.first
        self.hatches = self.bot.townhalls
        self.n_hatches = self.bot.townhalls.ready
        self.n_rdy_hatches = self.bot.townhalls.ready.amount

    async def build_queens(self, queens: []):
        """
        If a pool exists and bot can afford build a queen.

        :params: list of Queens
        """
        if (
            len(self.get_structure_count(self.pool_name)) == 1
            and len(queens) + self.bot.already_pending(UnitTypeId.QUEEN) < 6
        ):
            if self.bot.can_afford(UnitTypeId.QUEEN):
                for hatchery in self.bot.townhalls:
                    if hatchery.is_idle:
                        hatchery.train(UnitTypeId.QUEEN)

