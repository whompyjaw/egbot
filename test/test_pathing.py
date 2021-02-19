import unittest
from unittest import mock


import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.position import Point3

from MapAnalyzer import MapData


class PathBot(sc2.BotAI):
     def __init__(self):
         pass

     async def on_start(self):
          self.md = MapData(self)
         
          self.hq_pos = self.townhalls.first.position
          self.hq_pos3 = self.townhalls.first.position3d
          self.enemy_hq = self.enemy_start_locations[0]
          self.enemy_z_height = self.get_terrain_z_height(self.enemy_hq)
          self.enemy_hq_pos3 = Point3((self.enemy_hq.x, self.enemy_hq.y, self.enemy_z_height))
          self.plot_paths()


     def plot_paths(self):
          self.grid_points = self.md.get_pyastar_grid(default_weight=1.5)
          # self.paths = self.md.pathfind(self.hq_pos, self.enemy_hq, self.grid_points)
          # self.md.plot_influenced_path(start=self.hq_pos, goal=self.enemy_hq, weight_array=self.grid_points)
          # self.md.show()
          expacs = self.expansion_locations_list
          close_expac_list = sorted(self.get_distances(self.hq_pos, expacs), key=lambda x:x[0])
          
          '''
          Idea: Get closest expacs to hq (sorts by distance) - we need to spread creep between them.  Then we can find the furthest 
          expacs from our hq by simply returning the end of 'close_expac_list' i.e. close_expac_list[-5:].  This
          is a way for us to get the paths we want, possibly not the best way.  Next thought is to assign a queen
          a specific path via a specific queen policy.  
          '''

          for x in close_expac_list[:7]:
               loc = x[1]
               if self.hq_pos == loc:
                    continue
               # path = self.md.pathfind(self.hq_pos, loc, self.grid_points)
               self.md.plot_influenced_path(self.hq_pos, loc, self.grid_points)
          
          self.md.show()

     async def on_step(self, iteration):
          if iteration == 0:
               await self.client.debug_show_map()
               await self.client.debug_control_enemy()

               
          # self.client.debug_line_out(self.hq_pos3, self.enemy_hq_pos3, color=(255, 255, 255))
     def get_distances(self, point, iterable: list):
          dist_list = []

          for x in iterable:
               dist = self.distance_math_hypot(x, point)
               dist_list.append(tuple([dist, x]))

          return dist_list

run_game(
        maps.get("AbyssalReefLE"),
        [Bot(Race.Zerg, PathBot()), Computer(Race.Terran, Difficulty.VeryEasy)],
        realtime=False,
    )