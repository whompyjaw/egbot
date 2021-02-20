# from creepmgr import CreepManager
from combatmgr import CombatManager
from macromgr import MacroManager
from queens_sc2.queens import Queens
from queen_policy import QueenPolicy
from MapAnalyzer import MapData


class GeneralManager:
    def __init__(self, bot) -> None:
        self.bot = bot
        self.mm = MacroManager(bot)
        self.cm = CombatManager(bot)
        # self.cp = CreepManager(bot)

    async def manage(self) -> None:
        await self.mm.manage()
        await self.cm.manage()

    # async def setup_queen_policy(self):
    #     self.md = MapData(self)
    #     self.cp.setup_paths()
    #     self.qp = QueenPolicy(self, self.cp.ally_expac_paths)
    #     policy = self.qp.get_policy()
    #     self.bot.queens = Queens(self, True, policy)

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
