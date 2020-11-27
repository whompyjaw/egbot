import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer

class EGbot(sc2.BotAI):
    #Do these actions every step
    async def on_step(self, iteration):
        #built in method to distribute workers 16 to minerals, 3 to each gas geyser
        await self.distribute_workers()

#run game
run_game(maps.get("AbyssalReefLE"), [Bot(Race.Zerg, EGbot()), 
    Computer(Race.Terran, Difficulty.Easy)], realtime=True)