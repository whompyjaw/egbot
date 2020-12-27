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
from managers import MacroManager

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
        self.hatch_strat = random.randint(
            1, 3
        )
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
        await self.distribute_workers(1.0)
        await self.build_drones(larvae)
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

    # async def build_drones(self, larvae):
    #     # corrects game opening ->12:drone, 13:overlord, 14:drone, then 3 drones when OL pops
    #     if (
    #         larvae
    #         and self.can_afford(UnitTypeId.DRONE)
    #         and (self.supply_left > 1 or self.already_pending(UnitTypeId.OVERLORD) >= 1)
    #     ):
    #         if (
    #             self.supply_workers
    #             - self.worker_en_route_to_build(UnitTypeId.HATCHERY)
    #             + self.already_pending(UnitTypeId.DRONE)
    #         ) < (
    #             self.townhalls.amount + self.placeholders(UnitTypeId.HATCHERY).amount
    #         ) * 22:
    #             larva: Unit = larvae.random
    #             larva.train(UnitTypeId.DRONE)
    #             return

    async def build_overlords(self, larvae):
        """
        TODO: Will need to figure out if we need to create more than 200 supply OLs

        """
        # works with build_drones, ensures at game opening, only one OL is pending
        if self.supply_used <= 13 and self.already_pending(UnitTypeId.OVERLORD) < 1:
            larvae.random.train(UnitTypeId.OVERLORD)
        # after we're above 13 supply, complete the normal OL method
        elif (
            self.supply_cap > 14
            and self.supply_left < 2
            and larvae
            and self.can_afford(UnitTypeId.OVERLORD)
            and self.already_pending(UnitTypeId.OVERLORD) < 2
        ):
            larvae.random.train(UnitTypeId.OVERLORD)



        async def build_pool():  # Build spawning pool
            if (
                self.structures(UnitTypeId.SPAWNINGPOOL).amount
                + self.already_pending(UnitTypeId.SPAWNINGPOOL)
                == 0
            ):
                if self.can_afford(UnitTypeId.SPAWNINGPOOL):
                    await self.build(
                        UnitTypeId.SPAWNINGPOOL,
                        near=hq.position.towards(self.game_info.map_center, 5),
                    )

        async def expand():
            # Expands to nearest location when 300 minerals are available up to maximum 5 hatcheries
            if (
                self.townhalls.ready.amount + self.already_pending(UnitTypeId.HATCHERY)
                < 5
            ):
                if self.can_afford(UnitTypeId.HATCHERY):
                    await self.expand_now()

        async def build_gas():
            if self.can_afford(UnitTypeId.EXTRACTOR):
                # May crash if we dont have any drones
                for hatch in self.townhalls.ready:
                    for vg in self.vespene_geyser.closer_than(10, hatch):
                        if not self.worker_en_route_to_build(UnitTypeId.EXTRACTOR):
                            await self.build(UnitTypeId.EXTRACTOR, vg)
                            break

    def get_pos_around_unit(
        self, unit, min_range=0, max_range=500, step_size=1, loc_amt=32
    ):
        """
        TODO: need to fix loc_amt - despite having a value in there, get_pos_around_unit was retuning 70+ positions - could possibly be hard on system
        resources at a later date
        # e.g. loc_amt=4 would only consider 4 points: north, west, east, south
        """
        loc = unit.position.to2
        # loc = unit
        positions = [
            Point2(
                (
                    loc.x + distance * math.cos(math.pi * 2 * alpha / loc_amt),
                    loc.y + distance * math.sin(math.pi * 2 * alpha / loc_amt),
                )
            )
            for alpha in range(
                loc_amt
            )  # alpha is the angle here, locationAmount is the variable on how accurate the attempts look like a circle (= how many points on a circle)
            for distance in range(min_range, max_range + 1)
        ]  # distance depending on minrange and maxrange
        return positions

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
        ogging.debug(f"{unit.name} has completed.")

    async def build_queens(self):
        # larva queens
        if (
            self.structures(UnitTypeId.SPAWNINGPOOL).ready
            and self.queens.amount + self.already_pending(UnitTypeId.QUEEN) < 6
        ):
            if self.can_afford(UnitTypeId.QUEEN): 
                for (
                    hatchery
                ) in self.hatcheries:
                    if hatchery.is_idle:
                        hatchery.train(UnitTypeId.QUEEN)
                        self.assign_queen()

    def assign_queen(self, max_amount_inject_queens=3):
        # # list of all alive queens and bases, will be used for injecting
        if not hasattr(self, "queens_assigned_hatcheries"):
            self.queens_assigned_hatcheries = {}

        if max_amount_inject_queens == 0:
            self.queens_assigned_hatcheries = {}

        # if queen is done, move it to the closest hatch/lair/hive that doesnt have a queen assigned
        queens_no_inject_partner = self.units(UnitTypeId.QUEEN).filter(
            lambda q: q.tag not in self.queens_assigned_hatcheries.keys()
        )
        bases_no_inject_partner = self.townhalls.filter(
            lambda h: h.tag not in self.queens_assigned_hatcheries.values()
            and h.build_progress > 0.8
        )

        for queen in queens_no_inject_partner:
            if bases_no_inject_partner.amount == 0:
                break
            closest_base = bases_no_inject_partner.closest_to(queen)
            self.queens_assigned_hatcheries[queen.tag] = closest_base.tag
            bases_no_inject_partner = bases_no_inject_partner - [closest_base]
            break  # else one hatch gets assigned twice

    async def do_queen_injects(self, iteration):
        # list of all alive queens and bases, will be used for injecting
        alive_queen_tags = [
            queen.tag for queen in self.units(UnitTypeId.QUEEN)
        ]  # list of numbers (tags / unit IDs)
        alive_bases_tags = [base.tag for base in self.townhalls]

        # make queens inject if they have 25 or more energy
        to_remove_tags = []

        if hasattr(self, "queens_assigned_hatcheries"):
            for queen_tag, hatch_tag in self.queens_assigned_hatcheries.items():
                # queen is no longer alive
                if queen_tag not in alive_queen_tags:
                    to_remove_tags.append(queen_tag)
                    continue
                # hatchery / lair / hive is no longer alive
                if hatch_tag not in alive_bases_tags:
                    to_remove_tags.append(queen_tag)
                    continue
                # queen and base are alive, try to inject if queen has 25+ energy
                queen = self.units(UnitTypeId.QUEEN).find_by_tag(queen_tag)
                hatch = self.townhalls.find_by_tag(hatch_tag)
                if hatch.is_ready:
                    if (
                        queen.energy >= 25
                        and queen.is_idle
                        and not hatch.has_buff(BuffId.QUEENSPAWNLARVATIMER)
                    ):
                        queen(AbilityId.EFFECT_INJECTLARVA, hatch)
                else:
                    if (
                        iteration % self.inject_interval == 0
                        and queen.is_idle
                        and queen.position.distance_to(hatch.position) > 10
                    ):
                        queen(AbilityId.MOVE, hatch.position.to2)

            # clear queen tags (in case queen died or hatch got destroyed) from the dictionary outside the iteration loop
            for tag in to_remove_tags:
                self.queens_assigned_hatcheries.pop(tag)

    # TODO: Save this for later: # creep_queens: Units = self.units(UnitTypeId.QUEEN).closer_than(5.0, hq)

    def _get_close_queens(self, hatchery):
        return self.queens.closer_than(5.0, hatchery)

# Setting realtime=False makes the game/bot play as fast as possible
run_game(
    maps.get("AbyssalReefLE"),
    [Bot(Race.Zerg, EGbot()), Computer(Race.Terran, Difficulty.Easy)],
    realtime=False,
)
