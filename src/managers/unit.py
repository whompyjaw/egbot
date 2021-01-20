from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.position import Point2, Point3
from contextlib import suppress
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.unit import Unit
from sc2.units import Units
from queen import Queen
from managers.macro import MacroManager
from dicts import NestedDefaultDict
from units import Drone, Overlord, NewUnit


class UnitManager:
    def __init__(self, bot):
        self.bot = bot
        self.drone = UnitTypeId.DRONE
        self.larva = UnitTypeId.LARVA
        self.overlord = UnitTypeId.OVERLORD
        self.queen = UnitTypeId.QUEEN
        self.drone_name = "Drone"
        self.queen_name = "Queen"
        self.queen_home = {}
        self.mm = self.bot.mm
        self.queens = []
        self.units = NestedDefaultDict()
        self.larvae = []

    def update_units(self):
        self.larvae = self.bot.larva

    def add_unit(self, unit: Unit):
        """
        Adds the unit to specific list

        :params: Unit
        """
        if unit.name == 'Drone':
            new_unit = Drone(unit)
        elif unit.name == 'Overlord':
            new_unit = Overlord(unit)
        elif unit.name == 'Queen':
            new_unit = Queen(unit)
        else:
            new_unit = NewUnit(unit, 'Larva')
        
        self.units[new_unit.name][new_unit.tag] = new_unit

        if new_unit.name == self.queen_name:
            self.assign_queen(new_unit)
       


    def assign_queen(self, queen: Queen):
        """
        Assigns a queen as a Creep Queen or a Hatch Queen.  If Hatch Queen, assigns the queen to a specific hatchery for future larva injects
        
        :params Queen object:
        """        
        queens = self.units['Queen'].values()
        hatches = self.mm.structures['Hatchery'].values()
        # double check this
        bases_without_queens = Units([h for h in hatches if h.assigned_queen_tag == None], self.bot)

        if len(queens) == 1:
            queen.is_creep = True
        if len(queens) > 1 and bases_without_queens.amount >= 1:
            hatch_tag = bases_without_queens.closest_to(queen.position).tag
            closest_hatch = self.mm.structures['Hatchery'][hatch_tag]
            
            # Assign queen to hatch
            closest_hatch.assigned_queen_tag = queen.tag
            
            # assign hatch to queen
            queen.assigned_hatch_tag = hatch_tag
            queen.is_hatch = True
        else:
            queen.is_creep = True


    async def do_queen_injects(self):
        """
        Selects queen assign to specific and injects its assigned hatchery
        """
        queens = self.units['Queen'].values()
        for queen in queens:
            if queen.is_hatch and queen.energy >= 25 and queen.unit.is_idle:
                hatch = self.mm.structures['Hatchery'][queen.assigned_hatch_tag]
                queen.inject_larva(hatch.unit)
            




