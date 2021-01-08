class Queen:
    def __init__(self, unit):
        self.tag = unit.tag
        self.unit = unit
        self.is_defense = False
        self.is_creep = False
        self.is_hatch = False
        self.hatch_home = ''