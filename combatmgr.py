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
        pass
