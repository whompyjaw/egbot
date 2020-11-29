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
        larvae: Units = self.larva
        hq: Unit = self.townhalls.first
        
        # Build overlords if about to be supply blocked
        if (
            self.supply_left < 3
            and self.supply_cap < 200
            and self.already_pending(UnitTypeId.OVERLORD) < 2
            and self.can_afford(UnitTypeId.OVERLORD)
        ):
            self.train(UnitTypeId.OVERLORD)

        # If we have less than 22 drones, build drones
        # TODO: Will need to add an array or vector of buildings for "worker_en_route_to_build" to check instead of only HATCHERY
        # TODO: Check for max number of hatcheries
        if larvae and self.can_afford(UnitTypeId.DRONE): 
            if (self.supply_workers - self.worker_en_route_to_build(UnitTypeId.HATCHERY) + 
                self.already_pending(UnitTypeId.DRONE)) < (self.townhalls.amount + self.placeholders(UnitTypeId.HATCHERY).amount) * 22:
                larva: Unit = larvae.random
                larva.train(UnitTypeId.DRONE)
                return

        # Send workers across bases
        await self.distribute_workers(4)

        # Expands to nearest location when 300 minerals are available
        if self.can_afford(UnitTypeId.HATCHERY):
            # grabs next closest location
            location = await self.get_next_expansion()
            
            # takes availabe drone and orders to build a hatchery at location
            for drone in self.workers.collecting:
                drone: Unit
                drone.build(UnitTypeId.HATCHERY, location)
        
        # Send idle queens with >=25 energy to inject
        for queen in self.units(UnitTypeId.QUEEN).idle:
            # The following checks if the inject ability is in the queen abilitys - basically it checks if we have enough energy and if the ability is off-cooldown
            # abilities = await self.get_available_abilities(queen)
            # if AbilityId.EFFECT_INJECTLARVA in abilities:

            #TODO: implement a self.units(UnitTypeId.HATCHERY).closer_than(1.0, hatchery) - would mean if the queen is next to the hatchery it should inject at that 
            #hatchery only
            if queen.energy >= 25:
                queen(AbilityId.EFFECT_INJECTLARVA, hq)

        # Build spawning pool
        if self.structures(UnitTypeId.SPAWNINGPOOL).amount + self.already_pending(UnitTypeId.SPAWNINGPOOL) == 0:
            if self.can_afford(UnitTypeId.SPAWNINGPOOL):
                await self.build(UnitTypeId.SPAWNINGPOOL, near=hq.position.towards(self.game_info.map_center, 5))

        # If we dont have both extractors: build them
        # TODO: implement strategy here - really only need one extractor in the beginning
        if (self.structures(UnitTypeId.SPAWNINGPOOL) and self.gas_buildings.amount + 
            self.already_pending(UnitTypeId.EXTRACTOR) < 6):
            if self.can_afford(UnitTypeId.EXTRACTOR):
                # May crash if we dont have any drones
                for hatch in self.townhalls.ready:
                    for vg in self.vespene_geyser.closer_than(10, hatch):
                        drone: Unit = self.workers.random
                        drone.build_gas(vg)
                        break
                        

        # Saturate gas
        for a in self.gas_buildings:
            if a.assigned_harvesters < a.ideal_harvesters:
                w: Units = self.workers.closer_than(10, a)
                if w:
                    w.random.gather(a)

        
        '''
            Spawn Queens
                self.townhalls.ready is a list of hatcheries, once a hatchery is made it is added to the list:
                in the following syntax i.e. [Unit(name='Hatchery', tag=4376756226)], tags do not seem to be
                sequential, always begin with 43 though.

            Issues
                - issue here is since this is in a loop and each step of the program moves to the next hatchery (loops through each hatchery) a queen
                  gets made at whatever hatchery is identified when the below conditions are met.  
                  
                  In one game you could have all your queens made at the starting hatchery, in another, you could have the
                  first two queens at the starting hatchery (haven't corrected that yet), then a single queen 
                  spawning at each of the other hatcheries.
                  
                  One possible solution would be to associate the Queen with each Hatchery. Which could be done by using the unit's proximity functions.

            TODO: Create more queens than Hatcheries - support defense and creep spread
            TODO: Shorten "self.townhalls.second" - hq:beginning hatch, exp1 - first expansion, etc
        '''
        if self.structures(UnitTypeId.SPAWNINGPOOL).ready:
            for hatchery in self.townhalls.ready:
                if self.units(UnitTypeId.QUEEN).amount < len(self.townhalls.ready): # check the amount of queens vs the amount of hatcheries
                    if self.can_afford(UnitTypeId.QUEEN):
                        hatchery.train(UnitTypeId.QUEEN)
    
    # moves excess drones to next location
    # TODO: Possibly where we can create Queens upon building completion.
    async def on_building_construction_complete(self, unit: Unit):
        """ Set rally point of new hatcheries. """
        if unit.type_id == UnitTypeId.HATCHERY and self.mineral_field:
            mf = self.mineral_field.closest_to(unit)
            unit.smart(mf) # sets gathering location to mineral patch near recently built hatch

# Setting realtime=False makes the game/bot play as fast as possible
run_game(maps.get("AbyssalReefLE"), [Bot(Race.Zerg, EGbot()), 
    Computer(Race.Terran, Difficulty.Easy)], realtime=False)

