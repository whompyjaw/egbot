import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.ids.unit_typeid import UnitTypeId
from sc2.player import Bot, Computer
from sc2.unit import Unit
from sc2.units import Units
import logging
import random

from managers.economy.macro import MacroManager
from managers.unit import UnitManager

# importing from other folders
# from folder.folder.file import Whatever

logging.basicConfig(
    level=logging.DEBUG,
    filename="egbot.log",
    datefmt="%d-%m-%y %H:%M:%S",
    format="%(asctime)s | %(levelname)s | %(funcName)s | ln:%(lineno)d | %(message)s",
)


class EGbot(sc2.BotAI):
    def __init__(self):

        # self.hatch_strat = random.randint(1, 3)
        self.mm = MacroManager(self)
        self.um = UnitManager(self)

    async def on_step(self, iteration):
        self.iteration = iteration

        # Send workers across bases
        await self.mm.build_drone(self.um.larva)
        await self.mm.build_overlords(self.um.larva)
        # await self.distribute_workers(1.0)
        #        await self.opening_strats()
        #       await self.build_queens()
        #      await self.do_queen_injects(iteration)
        # await self.larva_inject()
        #     await self.spread_creep()

        """TODO: Think we should add in an early game tag, that once we're above X supply we move to mid game tag.  Early game tag has different
        parameters.  Example: if early_game: only build one gas geyser per hatchery, elif mid_game, build two.
        """

    async def on_building_construction_complete(self, unit: Unit):
        # TODO: Possibly where we can create Queens upon building completion.
        """ Set rally point of new hatcheries. """
        if unit.type_id == UnitTypeId.HATCHERY and self.mineral_field:
            mf = self.mineral_field.closest_to(unit)
            unit.smart(
                mf
            )  # sets gathering location to mineral patch near recently built hatch
        logging.debug(f"{unit.name} has completed.")
        self.mm.add_structure(unit)

    async def on_unit_created(self, unit):
        self.um.add_unit(unit)

run_game(
    """Setting realtime=False makes the game/bot play as fast as possible"""
    maps.get("AbyssalReefLE"),
    [Bot(Race.Zerg, EGbot()), Computer(Race.Terran, Difficulty.Easy)],
    realtime=False,
)
