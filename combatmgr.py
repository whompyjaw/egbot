"""
Managing overall attcking and defending for the bot/general manager
"""

from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.position import Point2, Point3
from scipy import spatial
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
from sc2.unit import Unit
from sc2.units import Units
from typing import Optional, Union
import numpy as np

import random


def _get_target_from_in_range_enemies(in_range_enemies: Units) -> Unit:
    if in_range_enemies.flying:
        lowest_hp: Unit = min(
            in_range_enemies.flying,
            key=lambda e: (e.health + e.shield, e.tag),
        )
    else:
        lowest_hp: Unit = min(
            in_range_enemies,
            key=lambda e: (e.health + e.shield, e.tag),
        )
    return lowest_hp


def find_closest_enemy(unit: Unit, enemies: Units) -> Optional[Unit]:
    """
    NOTE: Straight-outta RasperSc2 base_unit

    Find closest enemy because the built in python-sc2 version doesn't work with memory units.

    @param unit:
    @param enemies:
    @return:
    """
    if not unit or not enemies:
        return None

    distances = spatial.distance.cdist(
        np.array([e.position for e in enemies]),
        np.array([unit.position]),
        "sqeuclidean",
    )

    closest_enemy = min(
        ((unit, dist) for unit, dist in zip(enemies, distances)),
        key=lambda my_tuple: my_tuple[1],
    )[0]

    return closest_enemy


class CombatManager:
    def __init__(self, bot):
        self.bot = bot
        self.army = None
        self.army_types = []

    def setup(self):
        # TODO: I saw you had a dictionary, how come over a list? What value did you plan to pair with it?
        self.army_types = [UnitTypeId.ZERGLING, UnitTypeId.ROACH, UnitTypeId.BANELING,
                           UnitTypeId.HYDRALISK, UnitTypeId.MUTALISK, UnitTypeId.CORRUPTOR,
                           UnitTypeId.INFESTOR, UnitTypeId.ULTRALISK, UnitTypeId.BROODLORD,
                           UnitTypeId.SWARMHOSTMP, UnitTypeId.VIPER]

    async def manage(self):
        await self.update_army()
        await self._draw_debug()
        if len(self.army) >= 50:
            await self.attack_enemy()
            await self.micro_army(self.army, self.bot.enemy_units)
        elif self.bot.enemy_units:
            await self.micro_army(self.army, self.bot.enemy_units)
        else:
            # if len(self.army) < 40:
            if len(self.bot.townhalls) >= 3:
                await self.rally_army(self.bot.townhalls[2].position.towards(self.bot.game_info.map_center, 5))
            else:
                await self.rally_army(self.bot.main_base_ramp.bottom_center.towards(
                    self.bot.game_info.map_center, 3))

    async def attack_enemy(self):
        for unit in self.army.idle:
            unit.attack(self.calculate_attack())

    # TODO: Should this be async?
    def calculate_attack(self):
        if self.bot.enemy_structures:
            return random.choice(self.bot.enemy_structures).position
        return self.bot.enemy_start_locations[0]

    async def rally_army(self, point: Point2):
        for unit in self.army:
            unit.move(point)

    async def update_army(self):
        self.army = self.bot.units.of_type(self.army_types)

        return self.army

    async def micro_army(self, army: Units, enemy: Units) -> None:
        if not army or not enemy:
            return
        for unit in army:
            in_range_enemies: Units = self.in_attack_range_of(unit, enemy)
            if in_range_enemies:
                if unit.weapon_cooldown == 0:
                    target: Unit = _get_target_from_in_range_enemies(in_range_enemies)
                    unit.attack(target)
                else:
                    closest_enemy: Unit = find_closest_enemy(unit, in_range_enemies)
                    distance: float = (
                            unit.ground_range + unit.radius + closest_enemy.radius
                    )

                    unit.move(closest_enemy.position.towards(unit, distance))

            else:
                target = find_closest_enemy(unit, enemy)
                unit.attack(target)

    def in_attack_range_of(
            self, unit: Unit, enemies: Units, bonus_distance: Union[int, float] = 0
    ) -> Optional[Units]:
        """
        Get enemies in attack range of a given unit

        @param unit:
        @param enemies:
        @param bonus_distance:
        @return:
        """
        if not unit or not enemies:
            return None

        return enemies.filter(
            lambda e: self.target_in_range(unit, e, bonus_distance=bonus_distance)
        )

    def target_in_range(
            self, unit: Unit, target: Unit, bonus_distance: Union[int, float] = 0
    ) -> bool:
        """
        Check if the target is in range. Includes the target's radius when calculating distance to target.

        @param unit:
        @param target:
        @param bonus_distance:
        @return:
        """
        if unit.can_attack_ground and not target.is_flying:
            unit_attack_range = unit.ground_range
        elif unit.can_attack_air and (
                target.is_flying or target.type_id == UnitTypeId.COLOSSUS
        ):
            unit_attack_range = unit.air_range
        else:
            return False

        # noinspection PyProtectedMember
        return self.bot._distance_pos_to_pos(unit.position, target.position) <= (
                unit.radius + target.radius + unit_attack_range + bonus_distance
        )

    async def _draw_debug(self):
        if len(self.army) > 0:
            zerglings = [unit for unit in self.bot.units if unit.name == 'Zergling']
            hydras = [unit for unit in self.bot.units if unit.name == 'Hydralisk']
            drones = [unit for unit in self.bot.units if unit.name == 'Drone']
            queens = [unit for unit in self.bot.units if unit.name == 'Queen']
            supply_used = self.bot.supply_used

            self.bot.client.debug_text_screen(
                f"Drones: {str(len(drones)/supply_used)}\n \
                Zerglings: {str(len(zerglings)/supply_used)}\n \
                Hydralisks: {str(len(hydras)/supply_used)}\n \
                Queens: {str(len(hydras)/supply_used)}\n",
                pos=(0.2, 0.58),
                size=13,
                color=(0, 255, 255),
            )


    # TODO: Should we get rid of this?
    # def get_pos_around_unit(
    #     self, unit, min_range=0, max_range=500, step_size=1, loc_amt=32
    # ):
    #     """
    #     # e.g. loc_amt=4 would only consider 4 points: north, west, east, south
    #     """
    #     loc = unit.position.to2
    #     # loc = unit
    #     positions = [
    #         Point2(
    #             (
    #                 loc.x + distance * math.cos(math.pi * 2 * alpha / loc_amt),
    #                 loc.y + distance * math.sin(math.pi * 2 * alpha / loc_amt),
    #             )
    #         )
    #         for alpha in range(
    #             loc_amt
    #         )  # alpha is the angle here, locationAmount is the variable on how accurate the attempts look like a circle (= how many points on a circle)
    #         for distance in range(min_range, max_range + 1)
    #     ]  # distance depending on minrange and maxrange
    #     return positions
