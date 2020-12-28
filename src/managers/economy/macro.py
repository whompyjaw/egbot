import sc2
#from sc2 import run_game, maps, Race, Difficulty
from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.ids.buff_id import BuffId
#from sc2.player import Bot, Computer
from sc2.unit import Unit
from sc2.units import Units
from sc2.position import Point2, Point3
from typing import Union, Set
from units.drone import Drone
import logging
import random
import math

class MacroManager:

    macro_actions = []

    def __init__(self, bot):
        #larva: Unit = UnitTypeId.LARVA
        # self.larvae: Units = bot.UnitTypeId.LARVA
        self.drones = []
        self.drone = UnitTypeId.DRONE
        self.bot = bot
    
    async def build_drone(self, larvae):
    #corrects game opening ->12:drone, 13:overlord, 14:drone, then 3 drones when OL pops
        if (
            larvae
            and self.bot.can_afford(UnitTypeId.DRONE)

            and (self.bot.supply_left > 1 or self.bot.already_pending(UnitTypeId.OVERLORD) >= 1)
        ):
            if (
                self.bot.supply_workers
                - self.bot.worker_en_route_to_build(UnitTypeId.HATCHERY)
                + self.bot.already_pending(UnitTypeId.DRONE)
            ) < (
                self.bot.townhalls.amount + self.bot.placeholders(UnitTypeId.HATCHERY).amount
            ) * 22:
                larva: Unit = larvae.random
                larva.train(self.drone)
                self.drones.append(Drone(UnitTypeId.DRONE))
                return