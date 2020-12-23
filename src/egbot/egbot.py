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

logging.basicConfig(
    level=logging.DEBUG,
    filename="egbot.log",
    datefmt="%d-%m-%y %H:%M:%S",
    format="%(asctime)s | %(levelname)s | %(funcName)s | ln:%(lineno)d: %(message)s",
)


class EGbot(sc2.BotAI):
    def __init__(self):
        self.queensAssignedHatcheries = {}
        self.injectInterval = 100
        self.hatch_strat = random.randint(
            1, 3
        )

    async def on_step(self, iteration):
        self.hq: Unit = (
            self.townhalls.first
        )  # will need to account for if it's destroyed
        self.queens: Units = self.units(UnitTypeId.QUEEN)
        self.hatcheries = self.townhalls.ready
        self.iteration = iteration
        self.used_tumors: Set[int] = set()
        larvae: Units = self.larva
        """On_step actions"""
        # Send workers across bases
        await self.distribute_workers(1.0)
        await self.build_drones(larvae)
        await self.build_overlords(larvae)
        await self.opening_strats()
        await self.build_queens()
        await self.doQueenInjects(iteration)
        # await self.larva_inject()
        await self.spread_creep()

        """TODO: Think we should add in an early game tag, that once we're above X supply we move to mid game tag.  Early game tag has different
        parameters.  Example: if early_game: only build one gas geyser per hatchery, elif mid_game, build two.
        """

        # If we have less than 22 drones, build drones
        # TODO: Will need to add an array or vector of buildings for "worker_en_route_to_build" to check instead of only HATCHERY
        # TODO: Check for max number of hatcheries

    async def build_drones(self, larvae):
        # corrects game opening ->12:drone, 13:overlord, 14:drone, then 3 drones when OL pops
        if (
            larvae
            and self.can_afford(UnitTypeId.DRONE)
            and (self.supply_left > 1 or self.already_pending(UnitTypeId.OVERLORD) >= 1)
        ):
            if (
                self.supply_workers
                - self.worker_en_route_to_build(UnitTypeId.HATCHERY)
                + self.already_pending(UnitTypeId.DRONE)
            ) < (
                self.townhalls.amount + self.placeholders(UnitTypeId.HATCHERY).amount
            ) * 22:
                larva: Unit = larvae.random
                larva.train(UnitTypeId.DRONE)
                return

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

    """Starter method to develop strategies for various openings.  Uses a dictionary with different strategies
    to select from.  A random number is generated when the program starts determining the strategy.  
    """

    async def opening_strats(self):
        hq: Unit = self.townhalls.first
        strat_dict = {"pool_first": 1, "expand_first": 2, "double_expand": 3}

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

        # normal strat - let it play out
        if self.hatch_strat == strat_dict.get("pool_first"):
            await build_pool()
            if (
                self.already_pending(UnitTypeId.SPAWNINGPOOL) == 1
                and self.structures(UnitTypeId.EXTRACTOR).amount < 1
            ):
                await build_gas()
            await expand()
            if (
                self.townhalls.ready.amount == 2
                and self.structures(UnitTypeId.EXTRACTOR).amount < 3
            ):
                await build_gas()

        if self.hatch_strat == strat_dict.get("expand_first"):
            # expand as long as less than 2 hatcheries
            if (
                self.townhalls.ready.amount + self.already_pending(UnitTypeId.HATCHERY)
                < 2
            ):
                await expand()
            # elif to see if pool AND 2 hatcheries built, if so expand
            elif (
                self.structures(UnitTypeId.SPAWNINGPOOL).amount
                + self.already_pending(UnitTypeId.SPAWNINGPOOL)
                == 1
                and self.townhalls.ready.amount
                + self.already_pending(UnitTypeId.HATCHERY)
                == 2
            ):
                await expand()
            # if and elif are false, build pool
            else:
                await build_pool()
            # build a gas if pool is pending
            if (
                self.already_pending(UnitTypeId.SPAWNINGPOOL) == 1
                and self.structures(UnitTypeId.EXTRACTOR).amount < 1
            ):
                await build_gas()
            if (
                self.townhalls.ready.amount == 2
                and self.structures(UnitTypeId.EXTRACTOR).amount < 3
            ):
                await build_gas()

        if self.hatch_strat == strat_dict.get("double_expand"):
            # expand as long as less than 2 hatcheries
            if (
                self.townhalls.ready.amount + self.already_pending(UnitTypeId.HATCHERY)
                < 3
            ):
                await expand()
            # if pool built AND 3 hatcheries, continue to attempt to expand
            elif (
                self.structures(UnitTypeId.SPAWNINGPOOL).amount
                + self.already_pending(UnitTypeId.SPAWNINGPOOL)
                == 1
                and self.townhalls.ready.amount
                + self.already_pending(UnitTypeId.HATCHERY)
                == 3
            ):
                await expand()
            # if no pool built yet and 3 hatcheries pending or built, build pool
            else:
                await build_pool()

            # build a gas if pool is pending
            if (
                self.already_pending(UnitTypeId.SPAWNINGPOOL) == 1
                and self.structures(UnitTypeId.EXTRACTOR).amount < 1
            ):
                await build_gas()
            if (
                self.townhalls.ready.amount == 3
                and self.structures(UnitTypeId.EXTRACTOR).amount < 3
            ):
                await build_gas()

    # async def larva_inject(self):
    #     hatcheries = self.townhalls.ready #list of ready hatcheries
    #     queens = self.units(UnitTypeId.QUEEN)  # list of queens

    #     # TODO: use queen tags instead
    #     for hatchery in hatcheries:
    #         for queen in queens.closer_than(5.0, hatchery):
    #             if queen.energy >= 25:
    #                 queen(AbilityId.EFFECT_INJECTLARVA, hatchery)

    async def spread_creep(self):

        positions = []
        filtered_locations = []
        build_tumor = AbilityId.BUILD_CREEPTUMOR_QUEEN
        unused_tumors = []
        enemy_base = self.enemy_start_locations

        if hasattr(self, "queensAssignedHatcheries"):
            unassignedQueens = self.units(UnitTypeId.QUEEN).filter(
                lambda q: (
                    q.tag not in self.queensAssignedHatcheries
                    and q.energy >= 25
                    or q.energy >= 50
                )
                and (
                    q.is_idle
                    or len(q.orders) == 1
                    and q.orders[0].ability.id in [AbilityId.MOVE]
                )
            )
        else:
            unassignedQueens = self.units(UnitTypeId.QUEEN).filter(
                lambda q: q.energy >= 25
                and (
                    q.is_idle
                    or len(q.orders) == 1
                    and q.orders[0].ability.id in [AbilityId.MOVE]
                )
            )

        # queen
        for queen in unassignedQueens:
            positions = self.get_pos_around_unit(
                queen, min_range=5, max_range=10, loc_amt=12
            )

            # filter out places without creep
            for loc in positions:
                if self.has_creep(loc):
                    filtered_locations.append(loc)

                # find shortest distance to enemy base
            shortest_distance = 1000.00
            for loc in filtered_locations:
                temp_distance = math.sqrt(
                    (enemy_base[0].x - loc.x) ** 2.0 + (enemy_base[0].y - loc.y) ** 2.0
                )
                if temp_distance < shortest_distance:
                    best_loc = loc
                    shortest_distance = temp_distance

            queen(build_tumor, best_loc)

        """TODO: Determine directions for creep spread - still random, but only spreads outwards away from starting hatchery
            TODO: Ensure creep doesn't spread onto hatchery locations - potentially done"""

        filtered_locations = []  # locations to place tumors
        # all possible tumors
        tumors = (
            self.structures(UnitTypeId.CREEPTUMORQUEEN)
            | self.structures(UnitTypeId.CREEPTUMOR)
            | self.structures(UnitTypeId.CREEPTUMORBURROWED)
        )

        if tumors:  # if tumors exists
            all_tumors_abilities = await self.get_available_abilities(
                tumors
            )  # get all the abilities from available tumors
            for i, abilities in enumerate(
                all_tumors_abilities
            ):  # loop through tumors that have abilities
                tumor = tumors[i]  # select single tumor
                if not tumor.is_idle and isinstance(
                    tumor.order_target, Point2
                ):  # if tumor is in process of morphing or something, add to used.tumors
                    self.used_tumors.add(tumor.tag)
                    continue
                # ensure tumor has Ability to spread creep
                if AbilityId.BUILD_CREEPTUMOR_TUMOR in abilities:
                    # gets positions around tumor - note: loc_amt does not seem to work, returned over 70 positions last I checked
                    # max range seems too far as well - was getting out of range errors
                    positions = self.get_pos_around_unit(
                        tumor, min_range=5, max_range=20, loc_amt=12
                    )
                    # determine which positions have creep
                    for loc in positions:
                        if self.has_creep(loc) and not self.position_blocks_expansion(
                            loc
                        ):
                            # working towards sending creep out - this filters positions that are closer to the starting hatchery, so tumors don't go backwards, can go sideways though
                            if self._distance_pos_to_pos(
                                tumor.position, self.townhalls.first.position
                            ) <= self._distance_pos_to_pos(
                                loc, self.townhalls.first.position
                            ):
                                filtered_locations.append(loc)

                    pos = random.randrange(0, len(filtered_locations))
                    # build that tumor!
                    tumor(AbilityId.BUILD_CREEPTUMOR_TUMOR, filtered_locations[pos])

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

    """
    TODO: figure out why Union and self.expansion_locations_list say they have an error yet no issues arise in the code.  Suspect Pylint is goofed.
    Note: used pos: Union[Point2, Unit] instead of just pos: Point2 in attempt to fix a y is -1, self.height is 176 error.  Seems to work...
    """

    def position_blocks_expansion(self, pos: Union[Point2, Unit]) -> bool:
        blocks_expansion = False
        for expansion in self.expansion_locations_list:
            if pos.distance_to(expansion) < 6:
                blocks_expansion = True
                break
        return blocks_expansion

    # moves excess drones to next location
    # TODO: Possibly where we can create Queens upon building completion.
    async def on_building_construction_complete(self, unit: Unit):
        """ Set rally point of new hatcheries. """
        if unit.type_id == UnitTypeId.HATCHERY and self.mineral_field:
            mf = self.mineral_field.closest_to(unit)
            unit.smart(
                mf
            )  # sets gathering location to mineral patch near recently built hatch
        logging.debug(f"{unit.name} has completed.")

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
                        self.assignQueen()

    def assignQueen(self, maxAmountInjectQueens=3):
        # # list of all alive queens and bases, will be used for injecting
        if not hasattr(self, "queensAssignedHatcheries"):
            self.queensAssignedHatcheries = {}

        if maxAmountInjectQueens == 0:
            self.queensAssignedHatcheries = {}

        # if queen is done, move it to the closest hatch/lair/hive that doesnt have a queen assigned
        queensNoInjectPartner = self.units(UnitTypeId.QUEEN).filter(
            lambda q: q.tag not in self.queensAssignedHatcheries.keys()
        )
        basesNoInjectPartner = self.townhalls.filter(
            lambda h: h.tag not in self.queensAssignedHatcheries.values()
            and h.build_progress > 0.8
        )

        for queen in queensNoInjectPartner:
            if basesNoInjectPartner.amount == 0:
                break
            closestBase = basesNoInjectPartner.closest_to(queen)
            self.queensAssignedHatcheries[queen.tag] = closestBase.tag
            basesNoInjectPartner = basesNoInjectPartner - [closestBase]
            break  # else one hatch gets assigned twice

    async def doQueenInjects(self, iteration):
        # list of all alive queens and bases, will be used for injecting
        aliveQueenTags = [
            queen.tag for queen in self.units(UnitTypeId.QUEEN)
        ]  # list of numbers (tags / unit IDs)
        aliveBasesTags = [base.tag for base in self.townhalls]

        # make queens inject if they have 25 or more energy
        toRemoveTags = []

        if hasattr(self, "queensAssignedHatcheries"):
            for queenTag, hatchTag in self.queensAssignedHatcheries.items():
                # queen is no longer alive
                if queenTag not in aliveQueenTags:
                    toRemoveTags.append(queenTag)
                    continue
                # hatchery / lair / hive is no longer alive
                if hatchTag not in aliveBasesTags:
                    toRemoveTags.append(queenTag)
                    continue
                # queen and base are alive, try to inject if queen has 25+ energy
                queen = self.units(UnitTypeId.QUEEN).find_by_tag(queenTag)
                hatch = self.townhalls.find_by_tag(hatchTag)
                if hatch.is_ready:
                    if (
                        queen.energy >= 25
                        and queen.is_idle
                        and not hatch.has_buff(BuffId.QUEENSPAWNLARVATIMER)
                    ):
                        queen(AbilityId.EFFECT_INJECTLARVA, hatch)
                else:
                    if (
                        iteration % self.injectInterval == 0
                        and queen.is_idle
                        and queen.position.distance_to(hatch.position) > 10
                    ):
                        queen(AbilityId.MOVE, hatch.position.to2)

            # clear queen tags (in case queen died or hatch got destroyed) from the dictionary outside the iteration loop
            for tag in toRemoveTags:
                self.queensAssignedHatcheries.pop(tag)

    # TODO: Save this for later: # creep_queens: Units = self.units(UnitTypeId.QUEEN).closer_than(5.0, hq)

    def _get_close_queens(self, hatchery):
        return self.queens.closer_than(5.0, hatchery)


# Setting realtime=False makes the game/bot play as fast as possible
run_game(
    maps.get("AbyssalReefLE"),
    [Bot(Race.Zerg, EGbot()), Computer(Race.Terran, Difficulty.Easy)],
    realtime=False,
)
