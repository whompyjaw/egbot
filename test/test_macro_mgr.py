import pytest
import sc2
from eg
from sc2 import BotAI
from sc2.units import Units
from sc2.unit import Unit
from src.queen import Queen
from src.units import Drone, Overlord
from sc2.ids.unit_typeid import UnitTypeId
from src.managers.macro import MacroManager
from src.managers.unit import UnitManager
from src.dicts import NestedDefaultDict

    
# TODO: use pytest here
@pytest.fixture
def test_env():
    


@pytest.fixture
def unit_manager():
    return UnitManager()

@pytest.fixture
def units_dict():
    um = unit_manager()
    units = NestedDefaultDict()
    units['Drone'][123] = Drone()
    units['Drone'][1234] = Drone()
