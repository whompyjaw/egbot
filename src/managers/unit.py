import sc2
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.position import Point2, Point3
import sys, os
from contextlib import suppress
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.player import Bot, Computer
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2, Point3
from typing import Union, Set
import logging
import random
import math



class UnitManager():

    def __init__(self, bot):
        self.bot = bot

        self.drone = UnitTypeId.DRONE
        self.larva = UnitTypeId.LARVA

    
        self.drones = []
        self.creep_queens = []
        self.hatch_queens = []
        self.overlords = []
        self.larvae = []


    def add_unit(self, unit):
        if unit.name is self.drone.name:
            self.drones.append(unit)

            
    async def build_drone(self, unit_manager):
        # corrects game opening ->12:drone, 13:overlord, 14:drone, then 3 drones when OL pop
        if (
                (self.larvae
                 and self.bot.can_afford(self.drone)
                 and (self.bot.supply_left > 1
                      or self.bot.already_pending(UnitTypeId.OVERLORD)) >= 1)):
            if (
                    self.bot.supply_workers
                    - self.bot.worker_en_route_to_build(UnitTypeId.HATCHERY)
                    + self.bot.already_pending(UnitTypeId.DRONE)
            ) < (
                self.bot.townhalls.amount
                + self.bot.placeholders(UnitTypeId.HATCHERY).amount
            ) * 22:
            larva: Unit = self.larvae.random
            larva.train(self.drone)


    async def build_queens(self):
        # larva queens
        if (
            self.structures(UnitTypeId.SPAWNINGPOOL).ready
            and self.queens.amount + self.already_pending(UnitTypeId.QUEEN) < 6
        ):
            if self.can_afford(UnitTypeId.QUEEN): 
                for (
                    hatchery
                ) in self.hatcheries:
                    if hatchery.is_idle:
                        hatchery.train(UnitTypeId.QUEEN)
                        self.assign_queen()
            
            
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


    def assign_queen(self, max_amount_inject_queens=3):
    # # list of all alive queens and bases, will be used for injecting
        if not hasattr(self, "queens_assigned_hatcheries"):
            self.queens_assigned_hatcheries = {}

        if max_amount_inject_queens == 0:
            self.queens_assigned_hatcheries = {}

        # if queen is done, move it to the closest hatch/lair/hive that doesnt have a queen assigned
        queens_no_inject_partner = self.units(UnitTypeId.QUEEN).filter(
            lambda q: q.tag not in self.queens_assigned_hatcheries.keys()
        )
        bases_no_inject_partner = self.townhalls.filter(
            lambda h: h.tag not in self.queens_assigned_hatcheries.values()
            and h.build_progress > 0.8
        )

        for queen in queens_no_inject_partner:
            if bases_no_inject_partner.amount == 0:
                break
            closest_base = bases_no_inject_partner.closest_to(queen)
            self.queens_assigned_hatcheries[queen.tag] = closest_base.tag
            bases_no_inject_partner = bases_no_inject_partner - [closest_base]
            break  # else one hatch gets assigned twice

    async def do_queen_injects(self, iteration):
    # list of all alive queens and bases, will be used for injecting
        alive_queen_tags = [
            queen.tag for queen in self.units(UnitTypeId.QUEEN)
        ]  # list of numbers (tags / unit IDs)
        alive_bases_tags = [base.tag for base in self.townhalls]

        # make queens inject if they have 25 or more energy
        to_remove_tags = []

        if hasattr(self, "queens_assigned_hatcheries"):
            for queen_tag, hatch_tag in self.queens_assigned_hatcheries.items():
                # queen is no longer alive
                if queen_tag not in alive_queen_tags:
                    to_remove_tags.append(queen_tag)
                    continue
                # hatchery / lair / hive is no longer alive
                if hatch_tag not in alive_bases_tags:
                    to_remove_tags.append(queen_tag)
                    continue
                # queen and base are alive, try to inject if queen has 25+ energy
                queen = self.units(UnitTypeId.QUEEN).find_by_tag(queen_tag)
                hatch = self.townhalls.find_by_tag(hatch_tag)
                if hatch.is_ready:
                    if (
                        queen.energy >= 25
                        and queen.is_idle
                        and not hatch.has_buff(BuffId.QUEENSPAWNLARVATIMER)
                    ):
                        queen(AbilityId.EFFECT_INJECTLARVA, hatch)
                else:
                    if (
                        iteration % self.inject_interval == 0
                        and queen.is_idle
                        and queen.position.distance_to(hatch.position) > 10
                    ):
                        queen(AbilityId.MOVE, hatch.position.to2)

            # clear queen tags (in case queen died or hatch got destroyed) from the dictionary outside the iteration loop
            for tag in to_remove_tags:
                self.queens_assigned_hatcheries.pop(tag)

    # TODO: Save this for later: # creep_queens: Units = self.units(UnitTypeId.QUEEN).closer_than(5.0, hq)

    def _get_close_queens(self, hatchery):
        return self.queens.closer_than(5.0, hatchery)



    async def build_overlords(self, larvae):
        """
        TODO: Will need to figure out if we need to create more than 200 supply OLs

        """
        # works with build_drones, ensures at game opening, only one OL is pending
        if self.supply_used <= 13 and self.already_pending(UnitTypeId.OVERLORD) < 1:
            larvae.random.train(UnitTypeId.OVERLORD)
        # after we're above 13 supply, complete the normal OL method
        elif (
            self.supply_cap > 14
            and self.supply_left < 2
            and larvae
            and self.can_afford(UnitTypeId.OVERLORD)
            and self.already_pending(UnitTypeId.OVERLORD) < 2
        ):
            larvae.random.train(UnitTypeId.OVERLORD)

    async def build_drones(self, larvae):
        # corrects game opening ->12:drone, 13:overlord, 14:drone, then 3 drones when OL pops
        if (
            larvae
            and self.can_afford(UnitTypeId.DRONE)
            and (self.supply_left > 1 or self.already_pending(UnitTypeId.OVERLORD) >= 1)
        ):
            if (
                self.supply_workers
                - self.worker_en_route_to_build(UnitTypeId.HATCHERY)
                + self.already_pending(UnitTypeId.DRONE)
            ) < (
                self.townhalls.amount + self.placeholders(UnitTypeId.HATCHERY).amount
            ) * 22:
                larva: Unit = larvae.random
                larva.train(UnitTypeId.DRONE)
                return
