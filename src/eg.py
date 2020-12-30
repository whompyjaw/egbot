import sys, os
from contextlib import suppress
import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.player import Bot, Computer
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2, Point3
from typing import Union, Set
import logging
import random
import math

# from .egbot.src.managers.economy.macro import MacroManager
from managers.economy.macro import MacroManager

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
        self.queens_assigned_hatcheries = {}
        self.inject_interval = 100
        self.hatch_strat = random.randint(1, 3)
        self.mm = MacroManager(self)

    async def on_step(self, iteration):
        self.hq: Unit = (
            self.townhalls.first
        )  # will need to account for if it's destroyed
        self.queens: Units = self.units(UnitTypeId.QUEEN)
        self.hatcheries = self.townhalls.ready
        self.iteration = iteration
        self.used_tumors: Set[int] = set()

        larvae: Units = self.larva
        # Send workers across bases
        await self.mm.build_drone(larvae)
        await self.distribute_workers(1.0)
        await self.build_overlords(larvae)
        await self.opening_strats()
        await self.build_queens()
        await self.do_queen_injects(iteration)
        # await self.larva_inject()
        await self.spread_creep()

        """TODO: Think we should add in an early game tag, that once we're above X supply we move to mid game tag.  Early game tag has different
        parameters.  Example: if early_game: only build one gas geyser per hatchery, elif mid_game, build two.
        """

        # If we have less than 22 drones, build drones
        # TODO: Will need to add an array or vector of buildings for "worker_en_route_to_build" to check instead of only HATCHERY
        # TODO: Check for max number of hatcheries

    # async def expand():
    #     # Expands to nearest location when 300 minerals are available up to maximum 5 hatcheries
    #     if (
    #         self.townhalls.ready.amount + self.already_pending(UnitTypeId.HATCHERY)
    #         < 5
    #     ):
    #         if self.can_afford(UnitTypeId.HATCHERY):
    #             await self.expand_now()

    def _position_blocks_expansion(self, pos):
        """
        TODO: figure out why Union and self.expansion_locations_list say they have an error yet no issues arise in the code.  Suspect Pylint is goofed.
        Note: used pos: Union[Point2, Unit] instead of just pos: Point2 in attempt to fix a y is -1, self.height is 176 error.  Seems to work...

        From Glenn: You don't need to instantiate pos in this function because you're passing a position to this function. Python already knows what it is.
                    Also, put these docstring inside the function you are referring to.
                    we should do that for future TODO's as well.
        """

        blocks_expansion = False
        for expansion in self.expansion_locations_list:
            if pos.distance_to(expansion) < 6:
                blocks_expansion = True
                break
        return blocks_expansion

    async def on_building_construction_complete(self, unit: Unit):
        # TODO: Possibly where we can create Queens upon building completion.
        """ Set rally point of new hatcheries. """
        if unit.type_id == UnitTypeId.HATCHERY and self.mineral_field:
            mf = self.mineral_field.closest_to(unit)
            unit.smart(
                mf
            )  # sets gathering location to mineral patch near recently built hatch
        logging.debug(f"{unit.name} has completed.")


# Setting realtime=False makes the game/bot play as fast as possible
run_game(
    maps.get("AbyssalReefLE"),
    [Bot(Race.Zerg, EGbot()), Computer(Race.Terran, Difficulty.Easy)],
    realtime=False,
)
