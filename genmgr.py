from sc2.unit import UnitTypeId

from creepmgr import CreepManager
from combatmgr import CombatManager
from macromgr import MacroManager
from pathmgr import PathManager
from queens_sc2.queens import Queens
from queen_policy import QueenPolicy
from MapAnalyzer import MapData



class GeneralManager:
    def __init__(self, bot) -> None:
        self.bot = bot
        self.mm = MacroManager(bot)
        self.cm = CombatManager(bot)
        self.cp = CreepManager(bot)
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
        self.map_data = MapData(self.bot)
        self.setup_queens()
        self.pm.setup(self.map_data)
        self.cp.setup(self.pm)
        self.mm.setup()
        #self.cm.setup()

    async def manage(self, iteration: int) -> None:
        # TODO: It might be better to manaege iteration calls here
        await self.mm.manage()
        await self.cm.manage()
        if self.bot.iteration % 90 == 0 and self.bot.units(UnitTypeId.QUEEN):
            targets = self.cp.get_creep_targets()
            if targets:
                self.queens.update_creep_targets(targets)
        await self.queens.manage_queens(iteration)
        await self.build_queens()
        # if self.bot.units(UnitTypeId.QUEEN).amount == 2:
        #     await self.queens.set_new_policy(queen_policy=self.qp.mid_game_policy, reset_roles=True)

    def setup_queens(self):
        self.qp = QueenPolicy(self.bot)
        self.queens = Queens(self.bot, True, self.qp.queen_policy)

    async def build_queens(self) -> None:
        """
        If a pool exists and bot can afford build a queen.

        :params: Queens object
        """
        queen_count: int = self.bot.units(UnitTypeId.QUEEN).amount
        queens: Queens = self.queens

        # TODO: Probably want to keep this in case we update the queen count in the policy.
        cq: int = queens.policies.get('creep_policy').max_queens
        dq: int = queens.policies.get('defence_policy').max_queens
        iq: int = queens.policies.get('inject_policy').max_queens

        if (queen_count + self.bot.already_pending(UnitTypeId.QUEEN)) < (cq + dq + iq):
            if self.bot.structures(UnitTypeId.SPAWNINGPOOL).ready:
                if self.bot.can_afford(UnitTypeId.QUEEN):
                    for hatchery in self.bot.townhalls.ready:
                        if hatchery.is_idle:
                            hatchery.train(UnitTypeId.QUEEN)

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
