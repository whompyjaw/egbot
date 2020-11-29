import egbot

class DebugQueen:
    async def on_step(self, iteration):
        if iteration == 0:
            await self.client.debug_create_unit([UnitTypeId.HATCHERY, 1, self.expansion_locations[1], 1])
            await self.client.debug_create_unit([UnitTypeId.QUEEN, 1, self.expansion_locations[1].towards(5, self.game_info.map_center), 1])