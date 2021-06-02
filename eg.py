import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.ids.unit_typeid import UnitTypeId
from sc2.player import Bot, Computer
from sc2.unit import Unit
from genmgr import GeneralManager


class EGbot(sc2.BotAI):
    def __init__(self):
        super().__init__()
        self.gm = GeneralManager(self)
        self.iteration = 0

    async def on_start(self):
        self.gm.setup()

    async def on_step(self, iteration):
        self.iteration = iteration
        await self.gm.manage(iteration)

    async def on_before_start(self):
        mfs = self.mineral_field.closer_than(10, self.townhalls.random)
        for drone in self.units(UnitTypeId.DRONE):
            drone.gather(mfs.closest_to(drone))

    async def on_building_construction_complete(self, unit: Unit):
        if unit.type_id == UnitTypeId.HATCHERY:
            if self.mineral_field:
                mf = self.mineral_field.closest_to(unit)
                unit.smart(mf)

    async def on_unit_created(self, unit: Unit):
        pass

    async def on_unit_destroyed(self, unit_tag: int):
        self.gm.macromgr.queens.remove_unit(unit_tag)

    async def on_unit_type_changed(self, unit: Unit, previous_type: UnitTypeId):
        pass

    async def control_enemy(self):
        await self.client.debug_control_enemy()


def main():
    """Setting realtime=False makes the game/bot play as fast as possible"""
    run_game(
        maps.get("AbyssalReefLE"),
        [Bot(Race.Zerg, EGbot()), Computer(Race.Terran, Difficulty.Hard)],
        realtime=False,
    )


if __name__ == "__main__":
    main()
