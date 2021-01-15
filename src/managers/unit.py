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
        self.mm = MacroManager(self.bot)
        self.drones = []
        self.overlords = []
        self.queens = []
        self.larvae = []

    def update_units(self):
        self.larvae = self.bot.larva

    def add_unit(self, unit: Unit):
        """
        Adds the unit to specific list

        :params: Unit
        """
        if unit.name == self.drone_name:
            self.drones.append(unit)
        if unit.name == self.queen_name:
            new_queen = Queen(unit)
            self.queens.append(new_queen)
            self.assign_queen(new_queen)

    def assign_queen(self, queen: Queen):
        """
        Assigns a queen as a Creep Queen or a Hatch Queen.  If Hatch Queen, assigns the queen to a specific hatchery for future larva injects
        
        :params Queen object:
        """        
        queens_without_bases = [q for q in self.queens if not q.is_hatch]
        bases_without_queens = self.bot.townhalls.filter(lambda h: h.tag not in self.queen_home.values())

        if len(self.queens) == 1:
            queen.is_creep = True
        if len(self.queens) > 1 and len(bases_without_queens) >= 1:
            for queen in queens_without_bases:
                if not queen.is_creep: 
                    closest_base = bases_without_queens.closest_to(queen.position)
                    self.queen_home[queen.tag] = closest_base.tag #dict of queens and their hatches
                    queen.is_hatch = True
                    break
        else:
            queen.is_creep = True

    async def do_queen_injects(self):
        """
        Selects queen assign to specific and injects its assigned hatchery
        """
        for queen in self.queens:
            if queen.is_hatch and queen.energy >= 25 and queen.unit.is_idle:
                hatch = self.bot.townhalls.find_by_tag(self.queen_home.get(queen.tag))
                queen.inject_larva(hatch)
            




