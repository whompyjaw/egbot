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
        await self.distribute_workers()

        #Expands to nearest location when 300 minerals are available
        if self.can_afford(UnitTypeId.HATCHERY):
            #grabs next closest location
            location = await self.get_next_expansion()
            
            #takes availabe drone and orders to build a hatchery at location
            for drone in self.workers.collecting:
                drone: Unit
                drone.build(UnitTypeId.HATCHERY, location)

        # If all our townhalls are dead, send all our units to attack
        if not self.townhalls:
            for unit in self.units.of_type({UnitTypeId.DRONE, UnitTypeId.QUEEN, UnitTypeId.ZERGLING}):
                unit.attack(self.enemy_start_locations[0])
            return
        else:
            hq: Unit = self.townhalls.first
        
        # Send idle queens with >=25 energy to inject
        for queen in self.units(UnitTypeId.QUEEN).idle:
            # The following checks if the inject ability is in the queen abilitys - basically it checks if we have enough energy and if the ability is off-cooldown
            # abilities = await self.get_available_abilities(queen)
            # if AbilityId.EFFECT_INJECTLARVA in abilities:
            if queen.energy >= 25:
                queen(AbilityId.EFFECT_INJECTLARVA, hq)

        # Build spawning pool
        if self.structures(UnitTypeId.SPAWNINGPOOL).amount + self.already_pending(UnitTypeId.SPAWNINGPOOL) == 0:
            if self.can_afford(UnitTypeId.SPAWNINGPOOL):
                await self.build(UnitTypeId.SPAWNINGPOOL, near=hq.position.towards(self.game_info.map_center, 5))

                # If we dont have both extractors: build them
        if (self.structures(UnitTypeId.SPAWNINGPOOL) and self.gas_buildings.amount + 
            self.already_pending(UnitTypeId.EXTRACTOR) < 2):
            if self.can_afford(UnitTypeId.EXTRACTOR):
                # May crash if we dont have any drones
                for vg in self.vespene_geyser.closer_than(10, hq):
                    drone: Unit = self.workers.random
                    drone.build_gas(vg)
                    break


        # Saturate gas
        for a in self.gas_buildings:
            if a.assigned_harvesters < a.ideal_harvesters:
                w: Units = self.workers.closer_than(10, a)
                if w:
                    w.random.gather(a)

        # Build queen once the pool is done
        if self.structures(UnitTypeId.SPAWNINGPOOL).ready:
            if not self.units(UnitTypeId.QUEEN) and hq.is_idle:
                if self.can_afford(UnitTypeId.QUEEN):
                    hq.train(UnitTypeId.QUEEN)
            
    #moves excess drones to next location
    async def on_building_construction_complete(self, unit: Unit):
        """ Set rally point of new hatcheries. """
        if unit.type_id == UnitTypeId.HATCHERY and self.mineral_field:
            mf = self.mineral_field.closest_to(unit)
            unit.smart(mf)


#run game
run_game(maps.get("AbyssalReefLE"), [Bot(Race.Zerg, EGbot()), 
    Computer(Race.Terran, Difficulty.Easy)], realtime=True)

