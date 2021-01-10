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
        self.hatcheries = None
        self.mm = MacroManager(self.bot)
        self.drones = []
        # self.creep_queens = []
        # self.hatch_queens = []
        self.overlords = []
        self.queens = []
        # self.queens_assigned_hatcheries = {}
        self.larvae = []

    def update_units(self):
        self.larvae = self.bot.larva

    def add_unit(self, unit: Unit):
        """TODO: got to run, but found error: unit.name = 'Drone' or 'Queen' while self.drone.name = 'QUEEN'
        when we compare the two strings they will not be equal and therefore no drones or queens get appended.
        """
        if unit.name == self.drone_name:
            self.drones.append(unit)
        if unit.name == self.queen_name:
            new_queen = Queen(unit)
            self.queens.append(new_queen)
            self.assign_queen(new_queen)

    def assign_queen(self, queen: Queen):
        '''Assigns a queen as a Creep Queen or a Hatch Queen.  If Hatch Queen, assigns the queen to a specific hatchery for future larva injects '''
        queens_no_inject_partner = [q for q in self.queens if q.tag not in self.queen_home.keys()]
        bases_no_inject_partner = self.bot.townhalls.filter(lambda h: h.tag not in self.queen_home.values())

        if len(self.queens) == 1:
            queen.is_creep = True
        if len(self.queens) > 1 and bases_no_inject_partner.amount >= 1:
            for queen in queens_no_inject_partner:
                if not queen.is_creep: 
                    closest_base = bases_no_inject_partner.closest_to(queen.position)
                    self.queen_home[queen.tag] = closest_base.tag #dict of queens and their hatches
                    queen.hatch_home[queen.tag] = closest_base.tag #Queen object attribute
                    bases_no_inject_partner = bases_no_inject_partner - [closest_base]
                    queen.is_hatch = True
                    break
        else:
            queen.is_creep = True

    async def do_queen_injects(self):
        '''TODO: Need to further work below.  Works great BUT I want to use a Queen Object instead of
        Unit Object in queen'''
        for queen_tag, hatch_tag in self.queen_home.items():
            queen = self.bot.units(UnitTypeId.QUEEN).find_by_tag(queen_tag)
            hatch = self.bot.townhalls.find_by_tag(hatch_tag)

            if hatch.is_ready:
                if (queen.energy >= 25 and queen.is_idle
                    and not hatch.has_buff(BuffId.QUEENSPAWNLARVATIMER)):
                    queen(AbilityId.EFFECT_INJECTLARVA, hatch)
            else:
                if (queen.is_idle and queen.position.distance_to(hatch.position) > 10):
                    queen(AbilityId.MOVE, hatch.position.to2)



