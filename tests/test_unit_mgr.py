# from sc2 import BotAI
# from sc2.units import Units
# from sc2.unit import Unit
# from src.queen import Queen
# from sc2.ids.unit_typeid import UnitTypeId
from managers.unit_mgr import UnitManager
from collections import defaultdict
from units import Drone

def test_add_unit():
    new_drone_unit = Unit(UnitTypeId.DRONE)
    unit_tag = new_drone_unit.tag
    um = UnitManager(sc2.BotAI)
    um.add_unit(new_drone_unit)
    assert um.units['Drone'].get(unit_tag)