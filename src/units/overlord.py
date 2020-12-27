"""overlord stuff"""

from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.unit import Unit


class Overlord:
    def __init__(self, unit):
        self.tag = unit.tag
        self.unit = unit