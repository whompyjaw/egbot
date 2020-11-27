import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.ids.unit_typeid import UnitTypeId
from sc2.player import Bot, Computer
from sc2.unit import Unit
from sc2.units import Units

class EGbot(sc2.BotAI):
    #Do these actions every step
    async def on_step(self, iteration):
        
        # Build overlords if about to be supply blocked
        if (
            self.supply_left < 2
            and self.supply_cap < 200
            and self.already_pending(UnitTypeId.OVERLORD) < 2
            and self.can_afford(UnitTypeId.OVERLORD)
        ):
            self.train(UnitTypeId.OVERLORD)

        # While we have less than 16 drones, make more drones
        if (
            self.can_afford(UnitTypeId.DRONE)
            and self.supply_workers - self.worker_en_route_to_build(UnitTypeId.HATCHERY)
            < (self.townhalls.amount + self.placeholders(UnitTypeId.HATCHERY).amount) * 16
        ):
            self.train(UnitTypeId.DRONE)

        # Send workers across bases
        await self.distribute_workers()

#run game
run_game(maps.get("AbyssalReefLE"), [Bot(Race.Zerg, EGbot()), 
    Computer(Race.Terran, Difficulty.Easy)], realtime=True)

