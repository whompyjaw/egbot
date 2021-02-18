import unittest
from unittest import mock
from s2clientprotocol.sc2api_pb2 import VeryEasy

import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer

from MapAnalyzer import MapData


class PathBot(sc2.BotAI):
     def __init__(self):
         pass

     async def on_start(self):
          self.md = MapData(self)
          self.grid_points = self.md.get_pyastar_grid()
          self.hq = self.townhalls.first.position3d
          self.enemy_hq = self.enemy_start_locations[0].to3
          self.paths = self.md.pathfind(self.hq, self.enemy_hq, self.grid_points)
          self.client.debug_text_simple('inside on_start')
          
     async def on_step(self, iteration):
          if iteration == 0:
               await self.client.debug_show_map()
               await self.client.debug_control_enemy()
               
          
          self.client.debug_line_out(self.hq, self.enemy_hq, color=(255, 255, 0))
          self.client.debug_text_simple('THIS IS A TEST inside on_step')


run_game(
        maps.get("AbyssalReefLE"),
        [Bot(Race.Zerg, PathBot()), Computer(Race.Terran, Difficulty.VeryEasy)],
        realtime=False,
    )