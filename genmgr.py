from sc2.unit import UnitTypeId

from creepmgr import CreepManager
from combatmgr import CombatManager
from macromgr import MacroManager
from pathmgr import PathManager

from MapAnalyzer import MapData
from builds import *

class GeneralManager:
    def __init__(self, bot) -> None:
        self.bot = bot
        self.mm = MacroManager(bot)
        self.cm = CombatManager(bot)
        self.creepmgr = CreepManager(bot)
        self.pm = PathManager(bot)
        self.map_data = None
        self.queens = None
        self.qp = None

    def setup(self) -> None:
        """
        Setting MapData here in case we need to pass this to other managers.
        Though we could use a # function in PathManager: get_map_data, but I think this is fine

        Returns
        -------

        """
        # TODO: Choose random build here (eventually)
        self.map_data = MapData(self.bot)
        self.pm.setup(self.map_data)
        self.creepmgr.setup(self.pm)

        random_build = LingHydra(self.bot)
        self.mm.setup(random_build, self.creepmgr)
        self.cm.setup()

    async def manage(self, iteration: int) -> None:
        # TODO: It might be better to manaege iteration calls here
        await self.mm.manage()
        await self.cm.manage()

        # if self.bot.units(UnitTypeId.QUEEN).amount == 2:
        #     await self.queens.set_new_policy(queen_policy=self.qp.mid_game_policy, reset_roles=True)





# def get_pos_around_unit(
#     self, unit, min_range=0, max_range=500, step_size=1, loc_amt=32
# ):
#     """
#     TODO: need to fix loc_amt - despite having a value in there, get_pos_around_unit was retuning 70+ positions - could possibly be hard on system
#     resources at a later date
#     # e.g. loc_amt=4 would only consider 4 points: north, west, east, south
#     """
#     loc = unit.position.to2
#     # loc = unit
#     positions = [
#         Point2(
#             (
#                 loc.x + distance * math.cos(math.pi * 2 * alpha / loc_amt),
#                 loc.y + distance * math.sin(math.pi * 2 * alpha / loc_amt),
#             )
#         )
#         for alpha in range(
#             loc_amt
#         )  # alpha is the angle here, locationAmount is the variable on how accurate the attempts look like a circle (= how many points on a circle)
#         for distance in range(min_range, max_range + 1)
#     ]  # distance depending on minrange and maxrange
#     return positions
