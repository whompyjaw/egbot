from sc2.ids.ability_id import AbilityId
from units import NewUnit

class Queen(NewUnit):
    def __init__(self, unit):
        super().__init__(unit, 'Queen')
        self.is_defense = False
        self.is_creep = False
        self.is_hatch = False
        self.energy = unit.energy
        self.assigned_hatch_tag = None

    def inject_larva(self, hatch):
        self.unit(AbilityId.EFFECT_INJECTLARVA, hatch)

    def assign_hatch(self, hatch_tag):
        self.assigned_hatch = hatch_tag