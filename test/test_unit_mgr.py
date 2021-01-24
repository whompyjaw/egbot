from managers.unit_mgr import UnitManager
from collections import defaultdict
from units import Drone

# bot = EGBot()

# @pytest.fixture
# def unit_manager():
#     return UnitManager()

# @pytest.fixture
# def units_dict():
#     um = unit_manager()
#     units = NestedDefaultDict()
#     units['Drone'][123] = Drone()
#     units['Drone'][1234] = Drone()

def test_add_unit():
    bot = sc2.BotAI()
    new_unit = Unit(UnitTypeID.DRONE, bot)
    unit_tag = new_unit.tag
    um = UnitManager(bot)
    um.add_unit(new_unit)
    assert um.units['Drone'].get(unit_tag)
