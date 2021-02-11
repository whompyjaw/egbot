import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.ids.unit_typeid import UnitTypeId
from sc2.player import Bot, Computer
from sc2.unit import Unit
import logging
from genmgr import GeneralManager

# logging.basicConfig(
#     level=logging.DEBUG,
#     filename="egbot.log",
#     datefmt="%d-%m-%y %H:%M:%S",
#     format="%(asctime)s | %(levelname)s | %(funcName)s | ln:%(lineno)d | %(message)s",
# )


class EGbot(sc2.BotAI):
    def __init__(self):
        self.gm = GeneralManager(self)

    async def on_start(self):
        pass

    async def on_step(self, iteration):
        if iteration == 0:
            await self.chat_send("(glhf)")
        await self.gm.manage()

    async def on_before_start(self):
        mfs = self.mineral_field.closer_than(10, self.townhalls.random)
        for drone in self.units(UnitTypeId.DRONE):
            drone.gather(mfs.closest_to(drone))

    async def on_building_construction_complete(self, unit: Unit):
        pass

    async def on_unit_created(self, unit):
        pass

    async def on_unit_destroyed(self, unit_tag: int):
        pass

    async def on_unit_type_changed(self, unit: Unit, previous_type: UnitTypeId):
        pass


    """
    Can add all the accessory methods that we will need to get/set bot data
    For example: 
        def get_units(self, unittype) returns units of that specific type
        def get_zerglings(self):


    """

def main():
    """Setting realtime=False makes the game/bot play as fast as possible"""
    run_game(
        maps.get("AbyssalReefLE"),
        [Bot(Race.Zerg, EGbot()), Computer(Race.Terran, Difficulty.Easy)],
        realtime=False,
    )

if __name__ == "__main__":
    main()


