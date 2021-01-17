class SpawningPool:
    def __init__(self, unit):
        self.tag = unit.tag
        self.name = "SpawningPool"
        self.unit = unit
        self.position = unit.position

class Hatchery:
    def __init__(self, unit):
        self.tag = unit.tag
        self.name = 'Hatchery'
        self.unit = unit
        self.position = unit.position
        self.hq = False
        self.is_lair = False
        self.is_hive = False
        
class Extractor:
    def __init__(self, unit):
        self.tag = unit.tag
        self.name = "Extractor"
        self.unit = unit
        self.position = unit.position