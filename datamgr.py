from collections import defaultdict
from constants import *

from sc2.unit import Unit, UnitTypeId as id
from sc2.units import Units
import logging


logging.basicConfig(
    level=logging.DEBUG,
    filename="egbot.log",
    datefmt="%d-%m-%y %H:%M:%S",
    format="%(asctime)s | %(levelname)s | %(funcName)s | ln:%(lineno)d | %(message)s",
)

class DataManager:
    def __init__(self, bot) -> None:
        self.bot = bot

    def setup(self):
        pass

    async def log_worker_distribution(self) -> dict:
        wd = defaultdict()
        hq: Unit = self.bot.townhalls.first
        bases: Units = self.bot.townhalls.ready
        bases = bases.sorted_by_distance_to(self.bot.start_location)
        num_hatch = 1
        for base in bases:
            num_gas = 1
            hatch = 'hatch' + str(num_hatch)
            wd[hatch] = {}
            wd[hatch]['mining'] = base.assigned_harvesters
            vgs = self.bot.vespene_geyser.closer_than(10, base)
            for vg in vgs:
                wd[hatch]['gas' + str(num_gas)] = vg.assigned_harvesters
                num_gas += 1
            num_hatch += 1
        return wd

    async def log_unit_percentages(self, units: dict):
        unit_distributions = {}
        for unit, attributes in units.items():
            # calculate values for each unit
            unit_amt = self.bot.units(unit).amount + self.bot.already_pending(unit)
            distr = unit_amt * attributes.get(SUPPLY_COST) / 200
            unit_distributions[unit] = str(distr) + ' (' + str(unit_amt) + ')'

        logging.info(unit_distributions)

    async def get_res_collect_rate(self):
        # todo calculate this for governing when to spam units and when to not
        pass





# class DebugManager:
#     async def draw_unit_distribution(self):
#         self.bot.client.debug_text_screen(
#             f"Drones: {str(len(drones) / 200)}\n \
#             Zerglings: {str(len(zerglings) / 200)}\n \
#             Hydralisks: {str(len(hydras) / 200)}\n \
#             Queens: {str(len(queens) / 200)}\n",
#             pos=(0.2, 0.50),
#             size=13,
#             color=(0, 255, 255),
#         )
