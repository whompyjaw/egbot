from sc2.position import Point2
from typing import Union, List
from numpy import ndarray


class PathManager:
    def __init__(self, bot):
        self.bot = bot
        self.grid_points = []
        self.all_paths = []
        self.md = None
        self.ally_expac_paths_set = False
        self.enemy_expac_paths_set = False
        self.sorted_expacs = []
        self.hq_pos = (0, 0)
        self.ally_expac_paths = []
        self.paths_to_enemy = []
        self.num_ally_paths = []
        self.num_enemy_paths = []

    def setup(self, map_data):
        self.md = map_data
        self.hq_pos: Point2 = self.bot.townhalls.first.position
        self.grid_points: Union[ndarray, ndarray] = self.md.get_pyastar_grid()
        expacs = self.bot.expansion_locations_list
        self.sorted_expacs = sorted(self.get_distances_to(self.hq_pos, expacs), key=lambda expac: expac[0])

        self.num_ally_paths = int(len(expacs) / 2)  # rough estimate
        self.num_enemy_paths = len(expacs) - self.num_ally_paths

        # for x in self.sorted_expacs[:first_half]:
        #     loc = x[1]
        #     if self.hq_pos == loc:
        #         continue
        #     path = self.md.pathfind(self.hq_pos, loc, self.grid_points, sensitivity=7)
        #     self.ally_expac_paths.extend(path)
        self.build_paths_to_enemy()


    async def manage(self):
        pass

    def get_distances_to(self, start: Point2, targets: list) -> list:
        distances_to_target = []

        for target in targets:
            dist = self.bot.distance_math_hypot(start, target)
            distances_to_target.append([dist, target])

        return distances_to_target

    def build_paths_to_enemy(self):
        for x in self.sorted_expacs[self.num_enemy_paths:]:
            loc = x[1]
            if self.hq_pos == loc:
                continue
            path = self.md.pathfind(self.hq_pos, loc, self.grid_points, sensitivity=7)
            self.paths_to_enemy.extend(path)

