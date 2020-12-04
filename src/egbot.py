import sys,os
from contextlib import suppress

import numpy as np
from sc2.position import Point2, Point3


import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.player import Bot, Computer
from sc2.unit import Unit
from sc2.units import Units

class EGbot(sc2.BotAI):
    #Do these actions every step
    async def on_step(self, iteration):
        '''On_step actions'''
        # Send workers across bases
        await self.distribute_workers(1.0)
        await self.build_drones()
        await self.build_overlords()
        await self.expand()
        await self.build_spawning_pool()
        await self.build_queens()

        # If we have less than 22 drones, build drones
        # TODO: Will need to add an array or vector of buildings for "worker_en_route_to_build" to check instead of only HATCHERY
        # TODO: Check for max number of hatcheries
    async def build_drones(self):
        #variables
        larvae: Units = self.larva

        if larvae and self.can_afford(UnitTypeId.DRONE): 
            if (self.supply_workers - self.worker_en_route_to_build(UnitTypeId.HATCHERY) + 
                self.already_pending(UnitTypeId.DRONE)) < (self.townhalls.amount + self.placeholders(UnitTypeId.HATCHERY).amount) * 22:
                larva: Unit = larvae.random
                larva.train(UnitTypeId.DRONE)
                return
        
    async def build_overlords(self):
        # Build overlords if about to be supply blocked
        if (self.supply_left < 3 and self.supply_cap < 200
            and self.already_pending(UnitTypeId.OVERLORD) < 2
            and self.can_afford(UnitTypeId.OVERLORD)):
            self.train(UnitTypeId.OVERLORD)
  
    async def expand(self):
        # Expands to nearest location when 300 minerals are available up to maximum 3 hatcheries
        if self.townhalls.ready.amount + self.already_pending(UnitTypeId.HATCHERY) < 3:
            if self.can_afford(UnitTypeId.HATCHERY):
                await self.expand_now()

    async def build_spawning_pool(self):
        hq: Unit = self.townhalls.first
        # Build spawning pool
        if self.structures(UnitTypeId.SPAWNINGPOOL).amount + self.already_pending(UnitTypeId.SPAWNINGPOOL) == 0:
            if self.can_afford(UnitTypeId.SPAWNINGPOOL):
               await self.build(UnitTypeId.SPAWNINGPOOL, near=hq.position.towards(self.game_info.map_center, 5))

    async def build_queens(self):
        #list of hatcheries
        hatcheries = self.townhalls.ready #list of ready hatcheries
        queens = self.units(UnitTypeId.QUEEN)  # list of queens

        if self.structures(UnitTypeId.SPAWNINGPOOL).ready:
            #TODO: check if a hatchery has a queen close to it, if not, build queen
            if self.can_afford(UnitTypeId.QUEEN): #check to afford
                for hatchery in hatcheries: #loop through available hatcheries each step
                    close_queens = queens.closer_than(5.0, hatchery) #find list of queens close to hatchery
                    if not close_queens and self.already_pending(UnitTypeId.QUEEN)==0: 
                        '''TODO: test self.already_pending(UnitTypeId.QUEEN)==0:  as hatchery.self.already_pending(UnitTypeId.QUEEN)==0:
                        current problem is only one queen can be "birthing" at any given time no matter how many hatcheries you have.
                        TODO: add check for number of "queens", this current code will continue to make queens if they are moved
                        outside of the 5.0 distance
                        '''
                        #if no queens & one is not being made, train queen
                        hatchery.train(UnitTypeId.QUEEN)    
               
        # # Send idle queens with >=25 energy to inject
        # for queen in self.units(UnitTypeId.QUEEN).idle:
        #     # The following checks if the inject ability is in the queen abilitys - basically it checks if we have enough energy and if the ability is off-cooldown
        #     # abilities = await self.get_available_abilities(queen)
        #     # if AbilityId.EFFECT_INJECTLARVA in abilities:

        #     #TODO: implement a self.units(UnitTypeId.HATCHERY).closer_than(1.0, hatchery) - would mean if the queen is next to the hatchery it should inject at that 
        #     #hatchery only
        #     if queen.energy >= 25:
        #         queen(AbilityId.EFFECT_INJECTLARVA, hq)
        # # If we dont have both extractors: build them
        # # TODO: implement strategy here - really only need one extractor in the beginning
        # if (self.structures(UnitTypeId.SPAWNINGPOOL) and self.gas_buildings.amount + 
        #     self.already_pending(UnitTypeId.EXTRACTOR) < 6):
        #     if self.can_afford(UnitTypeId.EXTRACTOR):
        #         # May crash if we dont have any drones
        #         for hatch in self.townhalls.ready:
        #             for vg in self.vespene_geyser.closer_than(10, hatch):
        #                 drone: Unit = self.workers.random
        #                 drone.build_gas(vg)
        #                 break
                        

        # # Saturate gas
        # for a in self.gas_buildings:
        #     if a.assigned_harvesters < a.ideal_harvesters:
        #         w: Units = self.workers.closer_than(10, a)
        #         if w:
        #             w.random.gather(a)

    # moves excess drones to next location
    # TODO: Possibly where we can create Queens upon building completion.
    async def on_building_construction_complete(self, unit: Unit):
        """ Set rally point of new hatcheries. """
        if unit.type_id == UnitTypeId.HATCHERY and self.mineral_field:
            mf = self.mineral_field.closest_to(unit)
            unit.smart(mf) # sets gathering location to mineral patch near recently built hatch

# Setting realtime=False makes the game/bot play as fast as possible
run_game(maps.get("AbyssalReefLE"), [Bot(Race.Zerg, EGbot()), 
    Computer(Race.Terran, Difficulty.Easy)], realtime=True)

