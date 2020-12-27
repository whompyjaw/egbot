from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId


class Drone:
    def __init__(self, unit):
        self.tag = unit.tag
        self.unit = unit
        self.cost = 50
        
