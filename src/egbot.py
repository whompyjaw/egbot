import sys,os
from contextlib import suppress
import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.player import Bot, Computer
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2, Point3
import logging
import random

logging.basicConfig(level=logging.DEBUG, filename='egbot.log', datefmt='%d-%m-%y %H:%M:%S', format='%(asctime)s | %(levelname)s | %(funcName)s | ln:%(lineno)d: %(message)s')


class EGbot(sc2.BotAI):
    def __init__(self):
        self.creep_queen_tags = []
        self.larva_queen_tags = []
        self.defense_queens = [] # just created for fun
        self.hatch_strat = random.randint(1,3) # random number between 1-3 to determine strat at beginning of match
        


    #Do these actions every step
    async def on_step(self, iteration):
        self.hq: Unit = self.townhalls.first # will need to account for if it's destroyed
        self.queens: Units = self.units(UnitTypeId.QUEEN)
        self.hatcheries = self.townhalls.ready
        larvae: Units = self.larva
        '''On_step actions'''
        # Send workers across bases
        await self.distribute_workers(1.0)
        await self.build_drones(larvae)
        await self.build_overlords(larvae)
        await self.opening_strats()
        await self.build_queens()
        await self.larva_inject()
        await self.build_gas()
        await self.spread_creep()
        

        
        # If we have less than 22 drones, build drones
        # TODO: Will need to add an array or vector of buildings for "worker_en_route_to_build" to check instead of only HATCHERY
        # TODO: Check for max number of hatcheries
    async def build_drones(self, larvae):
        #variables
        if larvae and self.can_afford(UnitTypeId.DRONE): 
            if (self.supply_workers - self.worker_en_route_to_build(UnitTypeId.HATCHERY) + 
                self.already_pending(UnitTypeId.DRONE)) < (self.townhalls.amount + self.placeholders(UnitTypeId.HATCHERY).amount) * 22:
                larva: Unit = larvae.random
                larva.train(UnitTypeId.DRONE)
                return


    async def build_overlords(self, larvae):
        '''
            TODO: Will need to figure out if we need to create more than 200 supply OLs

        '''
        if (self.supply_left < 2 and larvae
            and self.can_afford(UnitTypeId.OVERLORD)
            and self.already_pending(UnitTypeId.OVERLORD) < 2):
            larvae.random.train(UnitTypeId.OVERLORD)
  
    '''Starter method to develop strategies for various openings.  Uses a dictionary with different strategies
    to select from.  A random number is generated when the program starts determining the strategy.  
    '''
    async def opening_strats(self):
        hq: Unit = self.townhalls.first
        strat_dict = {"pool_first":1, "expand_first":2,"double_expand":3}

        async def build_pool(): # Build spawning pool
            if self.structures(UnitTypeId.SPAWNINGPOOL).amount + self.already_pending(UnitTypeId.SPAWNINGPOOL) == 0:
                if self.can_afford(UnitTypeId.SPAWNINGPOOL):
                    await self.build(UnitTypeId.SPAWNINGPOOL, near=hq.position.towards(self.game_info.map_center, 5))
       
        async def expand():
            # Expands to nearest location when 300 minerals are available up to maximum 5 hatcheries
            if self.townhalls.ready.amount + self.already_pending(UnitTypeId.HATCHERY) < 5:
                if self.can_afford(UnitTypeId.HATCHERY):
                    await self.expand_now()

        #normal strat - let it play out
        if self.hatch_strat == strat_dict.get("pool_first"):
            await build_pool()
            await expand()

        if self.hatch_strat == strat_dict.get("expand_first"):
            #expand as long as less than 2 hatcheries
            if self.townhalls.ready.amount + self.already_pending(UnitTypeId.HATCHERY) < 2:
                await expand()
            #elif to see if pool AND 2 hatcheries built, if so expand
            elif self.structures(UnitTypeId.SPAWNINGPOOL).amount + self.already_pending(UnitTypeId.SPAWNINGPOOL) == 1 and \
                self.townhalls.ready.amount + self.already_pending(UnitTypeId.HATCHERY)==2:
                await expand()
            #if and elif are false, build pool
            else:
                await build_pool()
          
        if self.hatch_strat == strat_dict.get("double_expand"):
            #expand as long as less than 2 hatcheries
            if self.townhalls.ready.amount + self.already_pending(UnitTypeId.HATCHERY) < 3:
                await expand()
            #if pool built AND 3 hatcheries, continue to attempt to expand
            elif self.structures(UnitTypeId.SPAWNINGPOOL).amount + self.already_pending(UnitTypeId.SPAWNINGPOOL) == 1 and \
                self.townhalls.ready.amount + self.already_pending(UnitTypeId.HATCHERY)==3:
                await expand()
            #if no pool built yet and 3 hatcheries pending or built, build pool
            else:
                await build_pool()


    async def larva_inject(self):
        hatcheries = self.townhalls.ready #list of ready hatcheries
        queens = self.units(UnitTypeId.QUEEN)  # list of queens

        # TODO: use queen tags instead
        for hatchery in hatcheries:
            for queen in queens.closer_than(5.0, hatchery):
                if queen.energy >= 25:
                    queen(AbilityId.EFFECT_INJECTLARVA, hatchery)


    async def spread_creep(self):
        '''
            QUEEN
            select a queen from creep_tumors (find_by_tag)
            check if can cast creep tumor
            move queen to edge of creep
            place tumor

            TUMOR
            iterate through unused tumors 
            calculate place to plant tumor
            cast plant
            update unused_tumors for next check
        '''
        # build_tumor = AbilityId.BUILD_CREEPTUMOR_QUEEN
        # # creep_build_tumor = AbilityId.ZERGBUILD_CREEPTUMOR
        
        # # select queen
        # cqt = self.creep_queen_tags[0]
        # creep_queen = self.units.find_by_tag(cqt)
        # current_pos = creep_queen.position
        # # check if queen can cast creep tumor
        # if creep_queen.energy >= 25:
        #     # move queen to edge of creep
        #     creep_queen(build_tumor, 5)
            # cast tumor

        # move queen to edge of creep
        

        # creep_queens.append(second_hatch.train(UnitTypeId.QUEEN))
        # creep_queens[0](queen_build_tumor)
        # cq = creep_queens[0]
            
        # if cq.is_idle:
        #     cq(queen_build_tumor)
        # goto an area near the end of creep
        # build tumor
        
        pass
        # TODO: tumor spread


    #TODO: implement strategy here - really only need one extractor in the beginning
    async def build_gas(self):  
        if (self.structures(UnitTypeId.SPAWNINGPOOL) and self.gas_buildings.amount + 
            self.already_pending(UnitTypeId.EXTRACTOR) < 8):
            if self.can_afford(UnitTypeId.EXTRACTOR):
                # May crash if we dont have any drones
                for hatch in self.townhalls.ready:
                    for vg in self.vespene_geyser.closer_than(10, hatch):
                        drone: Unit = self.workers.random
                        drone.build_gas(vg)
                        break
                        
    # moves excess drones to next location
    # TODO: Possibly where we can create Queens upon building completion.
    async def on_building_construction_complete(self, unit: Unit):
        """ Set rally point of new hatcheries. """
        if unit.type_id == UnitTypeId.HATCHERY and self.mineral_field:
            mf = self.mineral_field.closest_to(unit)
            unit.smart(mf) # sets gathering location to mineral patch near recently built hatch
        logging.debug(f'{unit.name} has completed.')

    async def build_queens(self):
        # larva queens
        if self.structures(UnitTypeId.SPAWNINGPOOL).ready and self.queens.amount + self.already_pending(UnitTypeId.QUEEN) < 6:
            if self.can_afford(UnitTypeId.QUEEN): #check to afford
                for hatchery in self.hatcheries: # loop through available hatcheries each step
                    close_queens = self._get_close_queens(hatchery) #find list of queens close to hatchery
                    # if # of larva queens = 3 then build creep queen
                    if close_queens and hatchery.is_idle and len(self.larva_queen_tags) >= 3:
                        hatchery.train(UnitTypeId.QUEEN)
                    if not close_queens and hatchery.is_idle: # creates larva queen
                        hatchery.train(UnitTypeId.QUEEN)


    async def on_unit_created(self, unit: Unit):
        """ Override this in your bot class. This function is called when a unit is created."""
        if unit.type_id is UnitTypeId.QUEEN:
            if len(self.larva_queen_tags) < 3:
                self.larva_queen_tags.append(unit.tag)
            else:
                self.creep_queen_tags.append(unit.tag)
    
    
    async def on_unit_destroyed(self, unit_tag: int):
        if unit_tag in self.creep_queen_tags:
            self.creep_queen_tags.remove(unit_tag)
        if unit_tag in self.larva_queen_tags:
            self.larva_queen_tags.remove(unit_tag)
            

    # TODO: Save this for later: # creep_queens: Units = self.units(UnitTypeId.QUEEN).closer_than(5.0, hq)    


    def _get_close_queens(self, hatchery):
        return self.queens.closer_than(5.0, hatchery)
    

# Setting realtime=False makes the game/bot play as fast as possible
run_game(maps.get("AbyssalReefLE"), [Bot(Race.Zerg, EGbot()), 
    Computer(Race.Terran, Difficulty.Easy)], realtime=False)

