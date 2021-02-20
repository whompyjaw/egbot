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

from logger import Sc2Logger

logging.basicConfig(
    level=logging.DEBUG,
    filename="egbot.log",
    datefmt="%d-%m-%y %H:%M:%S",
    format="%(asctime)s | %(levelname)s | %(funcName)s | ln:%(lineno)d | %(message)s",
)


class EGbot(sc2.BotAI):
    def __init__(self):
        self.qp = None
        self.gm = GeneralManager(self)
        self.iteration = 0
        self.md = None
        self.queens = None
        self.logger = Sc2Logger()

    async def on_start(self):
        self.md = MapData(self)
        #self.gm.setup_queen_policy()
        self.hq_pos = self.townhalls.first.position
        self.grid_points = self.md.get_pyastar_grid()
        expacs = self.expansion_locations_list
        self.sorted_expacs = sorted(self.get_distances(self.hq_pos, expacs), key=lambda x:x[0])
        self.ally_expac_paths = []
        self.enemy_expac_paths = []
        self.total_paths = []
        self.creep_target_list = []
        self.filtered_expac_list = []
        
        first_half = int(len(expacs) / 2)
        second_half = len(expacs) - first_half

        for x in self.sorted_expacs[:first_half]:
            loc = x[1]
            if self.hq_pos == loc:
                continue
            # path = self.md.pathfind(self.hq_pos, loc, self.grid_points)
            path = self.md.pathfind(self.hq_pos, loc, self.grid_points, sensitivity=7)
            self.ally_expac_paths.extend(path)

        for x in self.sorted_expacs[14:]:
            loc = x[1]
            if self.hq_pos == loc:
                continue
            # path = self.md.pathfind(self.hq_pos, loc, self.grid_points)
            path = self.md.pathfind(self.hq_pos, loc, self.grid_points, sensitivity=7)
            self.enemy_expac_paths.extend(path)

        self.total_paths = self.ally_expac_paths + self.enemy_expac_paths

        self.filtered_expac_list = [pos for pos in (set(Point2(i) for i in self.total_paths))]

        for pos in self.filtered_expac_list:
            if not self.has_creep(pos):
                self.creep_target_list.append(pos)

        self.qp = QueenPolicy(self, self.creep_target_list)
        policy = self.qp.get_policy()
        self.queens = Queens(self, True, policy)


    async def on_step(self, iteration):
        self.iteration = iteration
        if iteration == 0:
            await self.chat_send("(glhf)")
        await self.gm.manage()
        await self.queens.manage_queens(iteration)
        await self.update_creep(iteration)
        # logging.info('Iteration: %s' % iteration)
        if self.iteration % 100 == 0:
            await self.log_info()


    def get_distances(self, point, iterable: list) -> list:
        dist_list = []

        for x in iterable:
            dist = self.distance_math_hypot(x, point)
            dist_list.append(tuple([dist, x]))

        return dist_list

    async def update_creep(self, iteration):
        self.target_list = []

        if iteration % 120 == 0:
            for pos in self.creep_target_list:
                if not self.has_creep(pos):
                    self.target_list.append(pos)

            self.queens.update_creep_targets(self.target_list)
        
        else:
            pass

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
        self.client.debug_control_enemy()

def main():
    """Setting realtime=False makes the game/bot play as fast as possible"""
    run_game(
        maps.get("AbyssalReefLE"),
        [Bot(Race.Zerg, EGbot()), Computer(Race.Terran, Difficulty.Easy)],
        realtime=False,
    )

if __name__ == "__main__":
    main()


