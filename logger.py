from collections import defaultdict

from sc2.unit import Unit
from sc2.units import Units

class Sc2Logger:
    def __init__(self) -> None:
        pass

    async def log_worker_distribution(self, bot) -> dict:
        wd = defaultdict()
        hq: Unit = bot.townhalls.first
        bases: Units = bot.townhalls.ready
        bases = bases.sorted_by_distance_to(bot.start_location)
        num_hatch = 1
        for base in bases:
            num_gas = 1
            hatch = 'hatch' + str(num_hatch)
            wd[hatch] = {}
            wd[hatch]['mining'] = base.assigned_harvesters
            vgs = bot.vespene_geyser.closer_than(10, base)
            for vg in vgs:
                wd[hatch]['gas' + str(num_gas)] = vg.assigned_harvesters
                num_gas += 1
            num_hatch += 1
        return wd