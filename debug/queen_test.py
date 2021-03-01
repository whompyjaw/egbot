mport sys, os
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
from genmgr import GeneralManager
from MapAnalyzer import MapData
from queens_sc2.queens import Queens
from queen_policy import QueenPolicy



class DebugQueen(sc2.BotAI):
    """
    Where we can test small problems within a vacuum
    """
    async def on_start(self):
        self.md = MapData(self)
        # logic: thinking we find paths to enemy base and then spread creep via that
        # TODO: Would we pass the list of paths to queen policy?
        self.grid_points = self.md.get_pyastar_grid()
        hq = self.townhalls.first.position
        enemy_hq = self.enemy_start_locations[0]


    async def on_step(self, iteration):
        if iteration == 0:
            await self.client.debug_show_map()
            # create queen at first hatch
            await self.client.debug_create_unit(
                [[UnitTypeId.QUEEN, 1, self.start_location, 1]]
            )
        




run_game(
    maps.get("AbyssalReefLE"),
    [Bot(Race.Zerg, DebugQueen()), Computer(Race.Terran, Difficulty.Easy)],
    realtime=False,
)


# Reference
# await self.client.debug_create_unit([[UnitTypeId.MARINE, 5, self._game_info.map_center, 1]])
