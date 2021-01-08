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
        '''TODO: Everything works EXCEPT queens_no_inject_partner - for some reason my list comprehension doesn't work
        The first queen through goes to .is_creep perferctly.  Second queen goes through and is matched with the closest
        hatchery and assigned .is_hatch.  I verified within queen.hatch_home that the queen tag is the key, and the hatch tag
        is the value.  However, when the third queen pops, queens_no_inject_partner still contains the previous .is_hatch 
        queen and thus the loop happens and hits the break with no action as that queen is already assigned.  Need to figure out
        how to remove queens already tagged to a hatch, thus I know my list comprehension is failing.'''
        queens_no_inject_partner = [q for q in self.queens if q.tag not in queen.hatch_home.keys()]
        bases_no_inject_partner = self.bot.townhalls.filter(lambda h: h.tag not in queen.hatch_home.values())

        if len(self.queens) == 1:
            queen.is_creep = True
        if len(self.queens) > 1:
            for queen in queens_no_inject_partner:
                if not queen.is_creep: 
                    if bases_no_inject_partner.amount == 0:
                        break
                    else:
                        closest_base = bases_no_inject_partner.closest_to(queen.position)
                        queen.hatch_home[queen.tag] = closest_base.tag
                        bases_no_inject_partner = bases_no_inject_partner - [closest_base]
                        queen.is_hatch = True
                        break


    # else one hatch gets assigned twice
        # if self.mm.n_rdy_hatches > 2:
        #     print("more than 2 hatches yo!")
        # if len(self.queens) > self.bot.townhalls.ready.amount:
        #     self.queens.append(queen)

    # def assign_queen(self, max_amount_inject_queens=3):
    #     # # list of all alive queens and bases, will be used for injecting
    #     if not hasattr(self, "queens_assigned_hatcheries"):
    #         self.queens_assigned_hatcheries = {}

    #     if max_amount_inject_queens == 0:
    #         self.queens_assigned_hatcheries = {}

    #     # if queen is done, move it to the closest hatch/lair/hive that doesnt have a queen assigned
    #     queens_no_inject_partner = self.units(UnitTypeId.QUEEN).filter(
    #         lambda q: q.tag not in self.queens_assigned_hatcheries.keys()
    #     )
    #     bases_no_inject_partner = self.townhalls.filter(
    #         lambda h: h.tag not in self.queens_assigned_hatcheries.values()
    #         and h.build_progress > 0.8
    #     )

    #     for queen in queens_no_inject_partner:
    #         if bases_no_inject_partner.amount == 0:
    #             break
    #         closest_base = bases_no_inject_partner.closest_to(queen)
    #         self.queens_assigned_hatcheries[queen.tag] = closest_base.tag
    #         bases_no_inject_partner = bases_no_inject_partner - [closest_base]
    #         break  # else one hatch gets assigned twice

    # async def do_queen_injects(self, iteration):
    #     # list of all alive queens and bases, will be used for injecting
    #     alive_queen_tags = [
    #         queen.tag for queen in self.units(UnitTypeId.QUEEN)
    #     ]  # list of numbers (tags / unit IDs)
    #     alive_bases_tags = [base.tag for base in self.townhalls]

    #     # make queens inject if they have 25 or more energy
    #     to_remove_tags = []

    #     if hasattr(self, "queens_assigned_hatcheries"):
    #         for queen_tag, hatch_tag in self.queens_assigned_hatcheries.items():
    #             # queen is no longer alive
    #             if queen_tag not in alive_queen_tags:
    #                 to_remove_tags.append(queen_tag)
    #                 continue
    #             # hatchery / lair / hive is no longer alive
    #             if hatch_tag not in alive_bases_tags:
    #                 to_remove_tags.append(queen_tag)
    #                 continue
    #             # queen and base are alive, try to inject if queen has 25+ energy
    #             queen = self.units(UnitTypeId.QUEEN).find_by_tag(queen_tag)
    #             hatch = self.townhalls.find_by_tag(hatch_tag)
    #             if hatch.is_ready:
    #                 if (
    #                     queen.energy >= 25
    #                     and queen.is_idle
    #                     and not hatch.has_buff(BuffId.QUEENSPAWNLARVATIMER)
    #                 ):
    #                     queen(AbilityId.EFFECT_INJECTLARVA, hatch)
    #             else:
    #                 if (
    #                     iteration % self.inject_interval == 0
    #                     and queen.is_idle
    #                     and queen.position.distance_to(hatch.position) > 10
    #                 ):
    #                     queen(AbilityId.MOVE, hatch.position.to2)

    #         # clear queen tags (in case queen died or hatch got destroyed) from the dictionary outside the iteration loop
    #         for tag in to_remove_tags:
    #             self.queens_assigned_hatcheries.pop(tag)

    # # TODO: Save this for later: # creep_queens: Units = self.units(UnitTypeId.QUEEN).closer_than(5.0, hq)

    # def _get_close_queens(self, hatchery):
    #     return self.queens.closer_than(5.0, hatchery)
