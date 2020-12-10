import sys, os
from contextlib import suppress
import sc2
import logging
import math
from sc2 import run_game, maps, Race, Difficulty
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.player import Bot, Computer
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2, Point3
from random import randrange


class DebugQueen(sc2.BotAI):
    """
    Where we can test small problems within a vacuum
    """

    async def on_step(self, iteration):
        if iteration == 0:
            await self.client.debug_show_map()
            # create queen at first hatch
            await self.client.debug_create_unit(
                [[UnitTypeId.QUEEN, 1, self.start_location, 1]]
            )
        await self.queen_spread_creep()

    async def queen_spread_creep(self):
        '''
            1. select queen
            2. get positions around queen (get_pos_around_unit)
            3. TODO: Need a better find if positions are placeable, no buildings, minerals, etc (can_place)
            4. check if those possible locations have creep (has_creep)
            5. 

        '''
        
        positions = []
        filtered_positions = []
        build_tumor = AbilityId.BUILD_CREEPTUMOR_QUEEN
        queens = self.units(UnitTypeId.QUEEN)
        
        for queen in queens:
            if queen.energy >= 25 and queen.is_idle: # i think i need to check if action not already in q
                positions = self.get_pos_around_unit(queen, min_range=5, max_range=10, loc_amt=16) 

                # filter out places without creep
                for loc in positions:
                    if self.has_creep(loc):
                        filtered_positions.append(loc)
                    
                queen(build_tumor, filtered_positions[randrange(len(filtered_positions))])


    def get_pos_around_unit(self, unit, min_range=0, max_range=500, step_size=1, loc_amt=32):
        '''
        # e.g. loc_amt=4 would only consider 4 points: north, west, east, south
        '''
        loc = unit.position.to2
        # loc = unit
        positions = [Point2(( \
            loc.x + distance * math.cos(math.pi * 2 * alpha / loc_amt), \
            loc.y + distance * math.sin(math.pi * 2 * alpha / loc_amt))) \
            for alpha in range(loc_amt) # alpha is the angle here, locationAmount is the variable on how accurate the attempts look like a circle (= how many points on a circle)
            for distance in range(min_range, max_range+1)] # distance depending on minrange and maxrange
        return positions
        
        

run_game(
    maps.get("AbyssalReefLE"),
    [Bot(Race.Zerg, DebugQueen()), Computer(Race.Terran, Difficulty.Easy)],
    realtime=False,
)


# Reference
# await self.client.debug_create_unit([[UnitTypeId.MARINE, 5, self._game_info.map_center, 1]])
