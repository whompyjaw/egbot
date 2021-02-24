import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.ids.unit_typeid import UnitTypeId
from sc2.player import Bot, Computer
from sc2.position import Point2
from sc2.unit import Unit
import logging
from genmgr import GeneralManager
from MapAnalyzer import MapData
from queens_sc2.queens import Queens
from queen_policy import QueenPolicy
from random import shuffle
from typing import Union
from numpy import ndarray

from logger import Sc2Logger

logging.basicConfig(
    level=logging.DEBUG,
    filename="egbot.log",
    datefmt="%d-%m-%y %H:%M:%S",
    format="%(asctime)s | %(levelname)s | %(funcName)s | ln:%(lineno)d | %(message)s",
)


class EGbot(sc2.BotAI):
    def __init__(self):
        super().__init__()
        self.qp = None
        self.gm = GeneralManager(self)
        self.iteration = 0
        self.md = None
        self.queens = None
        self.logger = Sc2Logger()
        self.ally_expac_paths = []
        self.enemy_expac_paths = []
        self.paths = []
        self.creep_target_list = []
        self.filtered_expac_list = []
        self.ally_expac_paths_set = False
        self.enemy_expac_paths_set = False
        self.sorted_expacs = []
        self.grid_points = []
        self.hq_pos = (0, 0)

    async def on_start(self):
        self.md = MapData(self)
        # self.gm.setup_queen_policy()
        self.hq_pos: Point2 = self.townhalls.first.position
        self.grid_points: Union[ndarray, ndarray] = self.md.get_pyastar_grid()
        expacs = self.expansion_locations_list
        self.sorted_expacs = sorted(self.get_distances(self.hq_pos, expacs), key=lambda expac: expac[0])

        first_half = int(len(expacs) / 2)
        second_half = len(expacs) - first_half

        self.qp = QueenPolicy(self, self.creep_target_list)
        self.queens = Queens(self, True, self.qp.queen_policy)

        for x in self.sorted_expacs[:first_half]:
            loc = x[1]
            if self.hq_pos == loc:
                continue
            path = self.md.pathfind(self.hq_pos, loc, self.grid_points, sensitivity=7)
            self.ally_expac_paths.extend(path)

        for x in self.sorted_expacs[second_half:]:
            loc = x[1]
            if self.hq_pos == loc:
                continue
            path = self.md.pathfind(self.hq_pos, loc, self.grid_points, sensitivity=7)
            self.enemy_expac_paths.extend(path)

    async def on_step(self, iteration):
        self.iteration = iteration
        if iteration == 0:
            await self.chat_send("(glhf)")
        await self.gm.manage()
        await self.queens.manage_queens(iteration)
        if iteration % 120 == 0:
            await self.update_creep()
            await self.log_info()

    def get_distances(self, start: Point2, targets: list) -> list:
        distances_to_target = []

        for target in targets:
            dist = self.distance_math_hypot(start, target)
            distances_to_target.append([dist, target])

        return distances_to_target

    async def update_creep(self):
        if not self.ally_expac_paths_set:
            self.ally_expac_paths_set = True
            self.paths = self.ally_expac_paths
            self.paths = set(self.paths)  # remove dups
        elif not self.enemy_expac_paths_set and self.queens.creep.creep_coverage >= 45.0:
            self.enemy_expac_paths_set = True
            self.paths = self.enemy_expac_paths
            self.paths = set(self.paths)  # remove dups

        target_list = []
        for pos in self.paths:
            # TODO: if pos is not within 10 units of tumor
            if not self.has_creep(pos):
                target_list.append(pos)

        shuffle(target_list)

        if target_list:
            self.queens.update_creep_targets(target_list)

    async def on_before_start(self):
        mfs = self.mineral_field.closer_than(10, self.townhalls.random)
        for drone in self.units(UnitTypeId.DRONE):
            drone.gather(mfs.closest_to(drone))

    async def on_building_construction_complete(self, unit: Unit):
        if unit.type_id == UnitTypeId.HATCHERY:
            if self.mineral_field:
                mf = self.mineral_field.closest_to(unit)
                unit.smart(mf)

    async def on_unit_created(self, unit: Unit):
        pass

    async def on_unit_destroyed(self, unit_tag: int):
        self.queens.remove_unit(unit_tag)
        pass

    async def on_unit_type_changed(self, unit: Unit, previous_type: UnitTypeId):
        pass

    async def log_info(self):
        res = await self.logger.log_worker_distribution(self)
        logging.info(res)

    async def control_enemy(self):
        await self.client.debug_control_enemy()


def main():
    """Setting realtime=False makes the game/bot play as fast as possible"""
    run_game(
        maps.get("AbyssalReefLE"),
        [Bot(Race.Zerg, EGbot()), Computer(Race.Terran, Difficulty.Easy)],
        realtime=False,
    )


if __name__ == "__main__":
    main()
