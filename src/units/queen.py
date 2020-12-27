import sc2
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.position import Point2, Point3


class Queen:
    def __init__(self, unit):
        self.tag = unit.tag
        self.unit = unit
        self.tumor = AbilityId.BUILD_CREEPTUMOR_TUMOR
        self.transfuse = AbilityId.TRANSFUSION_TRANSFUSION
        self.inject = AbilityId.EFFECT_INJECTLARVA
    # super().__init__()

    async def plant_tumor(self, loc):
        self.unit(self.tumor, loc)

    async def transfuse_unit(self, target):
        self.unit(self.transfuse, target)

    async def inject_larva(self, hatch):
        self.unit(self.inject, hatch)
        
           
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