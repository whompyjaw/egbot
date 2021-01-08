import unittest
import sc2
from sc2 import BotAI
from sc2.units import Units
from sc2.unit import Unit
from src.queen import Queen
from sc2.ids.unit_typeid import UnitTypeId
from src.managers.unit import UnitManager

class TestUnitManager(unittest.TestCase):
    def setUp(self):
        self.bot = BotAI()
        self.um = UnitManager()
        self.queen = Queen(self.bot.units(UnitTypeId.QUEEN))
        self.queens = [self.queen, self.queen, self.queen]

    def test_assign_queen(self):
        self.um.assign_queen(self.queen)
        pass

    def test_add_unit_queen(self):
        unit = self.bot.units(UnitTypeId.QUEEN)
        self.um.add_unit(unit)
        pass