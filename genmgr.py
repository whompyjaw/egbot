from sc2.unit import UnitTypeId

from creepmgr import CreepManager
from combatmgr import CombatManager
from macromgr import MacroManager
from pathmgr import PathManager

from MapAnalyzer import MapData
from builds import *

class GeneralManager:
    def __init__(self, bot) -> None:
        self.bot = bot
        self.mm = MacroManager(bot)
        self.cm = CombatManager(bot)
        self.creepmgr = CreepManager(bot)
        self.pm = PathManager(bot)
        self.map_data = None
        self.queens = None
        self.qp = None

    def setup(self) -> None:
        """
        Setting MapData here in case we need to pass this to other managers.
        Though we could use a # function in PathManager: get_map_data, but I think this is fine

        Returns
        -------

        """
        # TODO: Choose random build here (eventually)
        self.map_data = MapData(self.bot)
        self.pm.setup(self.map_data)
        self.creepmgr.setup(self.pm)

        random_build = LingHydra(self.bot)
        self.mm.setup(random_build, self.creepmgr)
        self.cm.setup()

    async def manage(self, iteration: int) -> None:
        # TODO: It might be better to manaege iteration calls here
        await self.mm.manage()
        await self.cm.manage()







