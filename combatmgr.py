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

import random


class CombatManager:
    def __init__(self, bot):
        self.bot = bot
        self.forces = None

    async def manage(self):
        await self.update_forces()
        if len(self.forces) >= 20:
            await self.attack_enemy()

    async def attack_enemy(self):
        for unit in self.forces.idle:
            unit.attack(self.calculate_attack())

    def calculate_attack(self):
        if self.bot.enemy_structures:
            return random.choice(self.bot.enemy_structures).position
        return self.bot.enemy_start_locations[0]

    async def update_forces(self):
        self.forces = self.bot.units.of_type({UnitTypeId.ZERGLING, UnitTypeId.ROACH, UnitTypeId.BANELING,
                                              UnitTypeId.HYDRALISK, UnitTypeId.MUTALISK, UnitTypeId.CORRUPTOR,
                                              UnitTypeId.INFESTOR, UnitTypeId.ULTRALISK, UnitTypeId.BROODLORD,
                                              UnitTypeId.SWARMHOSTMP, UnitTypeId.VIPER})

        return self.forces

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