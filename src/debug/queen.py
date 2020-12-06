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

class DebugQueen(sc2.BotAI):
    '''
        Where we can test small problems within a vacuum
    '''
    async def on_step(self, iteration):
        if iteration == 0:
            await self.client.debug_show_map()
            await self.client.debug_create_unit([[UnitTypeId.MARINE, 5, self._game_info.map_center, 1]])
            await self.client.debug_create_unit([[UnitTypeId.HATCHERY, 1, self._game_info.map_center, 1]])
            await self.client.debug_create_unit([[UnitTypeId.QUEEN, 1, self._game_info.map_center, 1]])


run_game(maps.get("AbyssalReefLE"), [Bot(Race.Zerg, DebugQueen()), 
    Computer(Race.Terran, Difficulty.Easy)], realtime=False)