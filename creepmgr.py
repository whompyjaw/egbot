from sc2.unit import UnitTypeId
from pathmgr import PathManager
from typing import List
from sc2.position import Point2


class CreepManager:
    def __init__(self, bot):
        self.bot = bot
        self.creep_target_list = []
        self.section_size = 0
        self.target_start = 0
        self.creep_paths = []
        self.filtered_creep_points = []

    def setup(self, pm: PathManager):
        self.creep_paths = pm.paths_to_enemy # can change this to any paths we want in future.
        self.filtered_creep_points = list(set(self.creep_paths)) # idk if we need this
        self.section_size = int(len(self.creep_paths) / 3)

    async def manage(self):
        return await self.update_creep()

    def get_creep_targets(self) -> List[Point2]:
        # if not self.ally_expac_paths_set:
        #     self.ally_expac_paths_set = True
        #     self.paths = list(set(self.ally_expac_paths))
        #     self.section_size = int(len(self.paths) / 3)
        # elif not self.enemy_expac_paths_set and self.queens.creep.creep_coverage >= 45.0:
        #     self.enemy_expac_paths_set = True
        #     self.paths = list(set(self.enemy_expac_paths))
        #     self.section_size = int(len(self.paths) / 3)

        if self.target_start >= len(self.creep_paths):
            self.target_start = 0
        path_points = self.filtered_creep_points[self.target_start: self.target_start + self.section_size]

        self.target_start += self.section_size

        creep_target_list = []
        for pos in path_points:
            # TODO: if pos is not within 10 units of tumor etc
            # might be something better to change in queens-sc2
            if not self.bot.has_creep(pos):
                creep_target_list.append(pos)

        # shuffle(target_list)


        return creep_target_list
