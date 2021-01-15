from sc2.ids.ability_id import AbilityId

class Queen:
    def __init__(self, unit):
        self.tag = unit.tag
        self.unit = unit
        self.position = unit.position
        self.is_defense = False
        self.is_creep = False
        self.is_hatch = False
        self.energy = unit.energy
        self.assigned_hatch = None

    def inject_larva(self, hatch):
        self.unit(AbilityId.EFFECT_INJECTLARVA, hatch)

    def assign_hatch(self, hatch_tag):
        self.assigned_hatch = hatch_tag