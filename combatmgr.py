"""
Managing overall attcking and defending for the bot/general manager
"""

from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.position import Point2, Point3
from contextlib import suppress
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.unit import Unit
from sc2.units import Units
from collections import defaultdict


class CombatManager:
    def __init__(self, bot):
        self.bot = bot

    async def manage(self):
        # self.calculate_attack()
        pass



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