


# class CreepManager:
#     def __init__(self, bot):
#         self.ally_expacs = []
#         self.enemy_expacs = []
#         self.bot = bot
#         self.sorted_expacs = []
#         self.ally_expac_paths = []
#         self.setup_paths()
        

#     async def manage(self):
#         pass


#     def setup_paths(self):
#         self.grid_points = self.md.get_pyastar_grid()
#         expacs = self.bot.expansion_locations_list
#         self.sorted_expacs = sorted(self.get_distances(self.hq_pos, expacs), key=lambda x:x[0])
#         self.sorted_expacs_pos = []
#         for xy in self.sorted_expacs:
#             self.sorted_expacs_pos.append(xy[1])
            
        
#         #
#         first_half = int(len(expacs) / 2)
#         second_half = len(expacs) - first_half

#         for x in self.sorted_expacs_pos[:first_half]:
#             loc = x[1]
#             if self.hq_pos == loc:
#                 continue
#             # path = self.md.pathfind(self.hq_pos, loc, self.grid_points)
#             path = self.bot.md.pathfind(self.hq_pos, loc, self.grid_points, sensitivity=7)
#             self.ally_expac_paths.append(path)
            



#         # # logic: thinking we find paths to enemy base and then spread creep via that
#         # # TODO: Would we pass the list of paths to queen policy?
#         # self.grid_points = self.md.get_pyastar_grid()

#         # await self.control_enemy()

#         # hq = self.townhalls.first.position
#         # enemy_hq = self.enemy_start_locations[0]
#         # creep_locs = self.expansion_locations_list

#         # for loc in creep_locs[:5]:
#         #     if loc == hq:
#         #         continue

#         #     self.paths = self.md.pathfind(hq, loc, self.grid_points, sensitivity = 7)

        
 
