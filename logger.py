from collections import defaultdict

class Sc2Logger:
    def __init__(self) -> None:
        self.worker_dirstribution = defaultdict()
        pass


    async def get_worker_distribution(self, bot) -> None:
        wd = self.worker_dirstribution
        wd['hatch_tag'] = 5
        wd[5]['min'] = 10
        wd[5]['gas1'] = 2
        wd[5]['gas2'] = 3
        if not bot.mineral_field or not bot.workers or not bot.townhalls.ready:
            return 
        gas_buildings = bot.gas_buildings.ready
        bases = self.bot.townhalls.ready
        workers_collecting_min = bot.units.collecting
        workers_gathering_min = bot.units.gathering
        for base in bases:
            workers_assigned = bot.unit(base.tag).assigned_harvesters

        for base in bases | gas_buildings:
            workers = base.harvesters

            local_minerals_tags = {
                        mineral.tag for mineral in self.mineral_field if mineral.distance_to(mining_place) <= 8
                    }