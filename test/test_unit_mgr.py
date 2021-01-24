import pytest
import sc2
from sc2 import BotAI
from sc2.units import Units

bot = EGBot()

@pytest.fixture
def unit_manager():
    return UnitManager()

@pytest.fixture
def units_dict():
    um = unit_manager()
    units = NestedDefaultDict()
    units['Drone'][123] = Drone()
    units['Drone'][1234] = Drone()
