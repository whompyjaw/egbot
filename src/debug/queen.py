import sys,os
from contextlib import suppress
import sc2
import logging
from sc2 import run_game, maps, Race, Difficulty
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.player import Bot, Computer
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2, Point3



class DebugQueen(sc2.BotAI):
    '''
        Where we can test small problems within a vacuum
    '''
    async def on_step(self, iteration):
        if iteration == 0:
            await self.client.debug_show_map()
            # create queen at first hatch
            await self.client.debug_create_unit([[UnitTypeId.QUEEN, 1, self.start_location, 1]])
        await self.spread_creep()
    async def spread_creep(self):
        build_tumor = AbilityId.BUILD_CREEPTUMOR_QUEEN
        queens = self.units(UnitTypeId.QUEEN)
        for queen in queens:
            if queen.energy >= 25:
                queen(build_tumor, 3)


run_game(maps.get("AbyssalReefLE"), [Bot(Race.Zerg, DebugQueen()), 
    Computer(Race.Terran, Difficulty.Easy)], realtime=False)


# Reference
# await self.client.debug_create_unit([[UnitTypeId.MARINE, 5, self._game_info.map_center, 1]])