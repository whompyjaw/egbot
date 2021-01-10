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
        self.hatch_home = {}

    def larva_inject(self, hatch):
        self.unit(AbilityId.EFFECT_INJECTLARVA, hatch)