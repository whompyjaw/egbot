from collections import defaultdict

from sc2.unit import Unit, UnitTypeId as id
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
        zerglings = self.bot.units(id.ZERGLING).amount + self.bot.already_pending(id.ZERGLING)
        #hydras = self.bot.units(id.HYDRALISK).amount + self.bot.already_pending(id.HYDRALISK)
        banelings = self.bot.units(id.BANELING).amount + self.bot.already_pending(id.BANELING)
        mutas = self.bot.units(id.MUTALISK).amount + self.bot.already_pending(id.MUTALISK)
        #drones = self.bot.units(id.DRONE).amount + self.bot.already_pending(id.DRONE)
        #queens = self.bot.units(id.QUEEN).amount + self.bot.already_pending(id.QUEEN)

        units = {
            #'drones': drones * 1 / 200,
            'lings': zerglings * 1 / 200,
           # 'hydras': hydras * 2 / 200,
           # 'queens': queens * 2/ 200,
            'mutas': mutas * 1 / 200,
            'banes': banelings * 1 / 200,
        }

        return units
