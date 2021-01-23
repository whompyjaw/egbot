class NewUnit:
    def __init__(self, unit, name):
        self.tag = unit.tag
        self.name = name
        self.unit = unit
        self.position = unit.position

class Drone(NewUnit):
    def __init__(self, unit):
        super().__init__(unit, 'Drone')

class Overlord(NewUnit):
    def __init__(self, unit):
        super().__init__(unit, 'Overlord')
        
class Zergling(NewUnit):
    def __init__(self, unit):
        super().__init__(unit, 'Zergling')

class Broodling(NewUnit):
    def __init__(self, unit):
        super().__init__(unit, 'Broodling')