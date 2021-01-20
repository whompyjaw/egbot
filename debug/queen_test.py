mport sys, os
from contextlib import suppress
import sc2
import logging
import math
from sc2 import run_game, maps, Race, Difficulty
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.player import Bot, Computer
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2, Point3
from random import randrange


class DebugQueen(sc2.BotAI):
    """
    Where we can test small problems within a vacuum
    """

    async def on_step(self, iteration):
        if iteration == 0:
            await self.client.debug_show_map()
            # create queen at first hatch
            await self.client.debug_create_unit(
                [[UnitTypeId.QUEEN, 1, self.start_location, 1]]
            )
        await self.queen_spread_creep()

    async def queen_spread_creep(self):
        """
                1. select queen
                2. get positions around queen (get_pos_around_unit)
                3. TODO: Need a better find if positions are placeable, no buildings, minerals, etc (can_place)
                    a. Push creep spread towards expansion (get enemy expansion then )
                4. check if those possible locations have creep (has_creep)
                5.


        get positions around unit
        then find the enemy base location
        use a method to filter out ideal positions closest to the enemies base
            1. Subtract all positions around queen from the enemies expansion location
                x2 -
            sqrt((x2-x1)^2-(y2-y1)^2)

         _distance_pos_to_pos
        """

        positions = []
        filtered_locations = []
        build_tumor = AbilityId.BUILD_CREEPTUMOR_QUEEN
        queens = self.units(UnitTypeId.QUEEN)
        enemy_base = self.enemy_start_locations

        for queen in queens:
            if (
                queen.energy >= 25 and queen.is_idle
            ):  # i think i need to check if action not already in q
                positions = self.get_pos_around_unit(
                    queen, min_range=5, max_range=10, loc_amt=12
                )

                # filter out places without creep
                for loc in positions:
                    if self.has_creep(loc):
                        filtered_locations.append(loc)

                # find shortest distance
                shortest_distance = 1000.00
                for loc in filtered_locations:
                    temp_distance = math.sqrt(
                        (enemy_base[0].x - loc.x) ** 2.0
                        + (enemy_base[0].y - loc.y) ** 2.0
                    )
                    if temp_distance < shortest_distance:
                        best_loc = loc
                        shortest_distance = temp_distance

                queen(build_tumor, best_loc)

    def get_pos_around_unit(
        self, unit, min_range=0, max_range=500, step_size=1, loc_amt=32
    ):
        """
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


run_game(
    maps.get("AbyssalReefLE"),
    [Bot(Race.Zerg, DebugQueen()), Computer(Race.Terran, Difficulty.Easy)],
    realtime=False,
)


# Reference
# await self.client.debug_create_unit([[UnitTypeId.MARINE, 5, self._game_info.map_center, 1]])
