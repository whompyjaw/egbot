from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.position import Point2, Point3
from contextlib import suppress
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.unit import Unit
from sc2.units import Units


class UnitManager:
    def __init__(self, bot):
        self.bot = bot

        self.drone = UnitTypeId.DRONE
        self.larva = UnitTypeId.LARVA
        self.overlord = UnitTypeId.OVERLORD
        self.queen = UnitTypeId.QUEEN
        self.drone_name = "DRONE"
        self.queen_name = "QUEEN"

        self.drones = []
        self.creep_queens = []
        self.hatch_queens = []
        self.overlords = []
        self.queens = []
        self.queens_assigned_hatcheries = {}
        self.larvae = []

    def update_larva(self):
        self.larvae = self.bot.larva

    def add_unit(self, unit):
        """TODO: got to run, but found error: unit.name = 'Drone' or 'Queen' while self.drone.name = 'QUEEN'
        when we compare the two strings they will not be equal and therefore no drones or queens get appended.
        
        1/3/2021
        From Glenn: because self.drone is only UnitTypeId. Which dosen't have the property "name". Only a Unit object does.
        So, we could create another variable "self.drone_name = "DRONE" as I did above.
        
        We could use own own custom unit objects to hold their names, but I think it's better (to avoid that stuff)
        we can create an object or enumerate: UnitNames and put all the names there i.e:
        class UnitNames:
            self.drone = "DRONE"
            self.queen = "QUEEN"

        UnitNames = {
            drone = "DRONE"
            queen = "QUEEN"
        }
        I think that is syntax of enumerate

        This would be an object:
          unit_name = UnitNames()
          unit_name.drone

        You prolly wonder why do this, but it just helps prevent typos since linters don't check strings.
        """
        if unit.name is self.drone_name:
            self.drones.append(unit)
        if unit.name is self.queen_name:
            """First queen to lay creep, then queens assigned based on how many hatcheries"""
            # Don't we want firt queen to be a hatch queen?
            if len(self.queens) == 0:
                self.creep_queens.append(unit)
                self.queens.append(unit)
            if len(self.queens) <= self.bot.townhalls.ready and len(self.queens) >= 1:
                self.hatch_queens.append(unit)
                self.queens.append(unit)
            else:
                self.creep_queens.append(unit)
                self.queens.append(unit)

            # positions = []
            # filtered_locations = []
            # unused_tumors = []
            # enemy_base = BotAI.enemy_start_locations

            # if hasattr(self, "queens_assigned_hatcheries"):
            #     unassignedQueens = self.units(UnitTypeId.QUEEN).filter(
            #         lambda q: (
            #             q.tag not in self.queens_assigned_hatcheries
            #             and q.energy >= 25
            #             or q.energy >= 50
            #         )
            #         and (
            #             q.is_idle
            #             or len(q.orders) == 1
            #             and q.orders[0].ability.id in [AbilityId.MOVE]
            #         )
            #     )
            # else:
            #     unassignedQueens = self.units(UnitTypeId.QUEEN).filter(
            #         lambda q: q.energy >= 25
            #         and (
            #             q.is_idle
            #             or len(q.orders) == 1
            #             and q.orders[0].ability.id in [AbilityId.MOVE]
            #         )
            #     )

            # # queen
            # for queen in unassignedQueens:
            #     positions = self.get_pos_around_unit(
            #         queen, min_range=5, max_range=10, loc_amt=12
            #     )

            #     # filter out places without creep
            #     for loc in positions:
            #         if self.has_creep(loc):
            #             filtered_locations.append(loc)

            #         # find shortest distance to enemy base
            #     shortest_distance = 1000.00
            #     for loc in filtered_locations:
            #         temp_distance = math.sqrt(
            #             (enemy_base[0].x - loc.x) ** 2.0 + (enemy_base[0].y - loc.y) ** 2.0
            #         )
            #         if temp_distance < shortest_distance:
            #             best_loc = loc
            #             shortest_distance = temp_distance
            # queen(build_tumor, loc)

            """ 
                TODO: Determine directions for creep spread - still random, but only spreads outwards away from starting hatchery
                TODO: Ensure creep doesn't spread onto hatchery locations - potentially done
            """

            # filtered_locations = []  # locations to place tumors
            # # all possible tumors
            # tumors = (
            #     self.structures(UnitTypeId.CREEPTUMORQUEEN)
            #     | self.structures(UnitTypeId.CREEPTUMOR)
            #     | self.structures(UnitTypeId.CREEPTUMORBURROWED)
            # )

            # if tumors:  # if tumors exists

            #     all_tumors_abilities = await self.get_available_abilities(
            #         tumors
            #     )  # get all the abilities from available tumors
            #     for i, abilities in enumerate(
            #         all_tumors_abilities
            #     ):  # loop through tumors that have abilities
            #         tumor = tumors[i]  # select single tumor
            #         if not tumor.is_idle and isinstance(
            #             tumor.order_target, Point2
            #         ):  # if tumor is in process of morphing or something, add to used.tumors
            #             self.used_tumors.add(tumor.tag)
            #             continue
            #         # ensure tumor has Ability to spread creep
            #         if AbilityId.BUILD_CREEPTUMOR_TUMOR in abilities:
            #             # gets positions around tumor - note: loc_amt does not seem to work, returned over 70 positions last I checked
            #             # max range seems too far as well - was getting out of range errors
            #             positions = self.get_pos_around_unit(
            #                 tumor, min_range=5, max_range=20, loc_amt=12
            #             )
            #             # determine which positions have creep
            #             for loc in positions:
            #                 if self.has_creep(loc) and not self._position_blocks_expansion(
            #                     loc
            #                 ):
            #                     # working towards sending creep out - this filters positions that are closer to the starting hatchery, so tumors don't go backwards, can go sideways though
            #                     if self._distance_pos_to_pos(
            #                         tumor.position, self.townhalls.first.position
            #                     ) <= self._distance_pos_to_pos(
            #                         loc, self.townhalls.first.position
            #                     ):
            #                         filtered_locations.append(loc)

            #             pos = random.randrange(0, len(filtered_locations))
            #             # build that tumor!
            #             tumor(AbilityId.BUILD_CREEPTUMOR_TUMOR, filtered_locations[pos])

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
