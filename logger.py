from collections import defaultdict

from sc2.unit import Unit
from sc2.units import Units

class Sc2Logger:
    def __init__(self, bot) -> None:
        self.bot = bot
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

    async def log_unit_percentages(self) -> dict:
        zerglings = [unit for unit in self.bot.units if unit.name == 'Zergling']
        hydras = [unit for unit in self.bot.units if unit.name == 'Hydralisk']
        drones = [unit for unit in self.bot.units if unit.name == 'Drone']
        queens = [unit for unit in self.bot.units if unit.name == 'Queen']

        units = {
            'drones': len(drones) / 200,
            'lings': len(zerglings) / 200,
            'hydras': len(hydras) / 200,
            'queens': len(queens) / 200,
        }

        return units
