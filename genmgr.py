from combatmgr import CombatManager
from macromgr import MacroManager
from combatmgr import CombatManager


class GeneralManager:
    def __init__(self, bot) -> None:
        self.mm = MacroManager(bot)
        self.cm = CombatManager(bot)

    async def manage(self) -> None:
        await self.mm.manage()
        await self.cm.manage()



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
