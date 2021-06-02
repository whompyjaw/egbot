from creepmgr import CreepManager
from combatmgr import CombatManager
from macromgr import MacroManager
from pathmgr import PathManager
from datamgr import DataManager

from MapAnalyzer import MapData


class GeneralManager:
    def __init__(self, bot) -> None:
        self.bot = bot
        self.macromgr = MacroManager(bot)
        self.combatmgr = CombatManager(bot)
        self.creepmgr = CreepManager(bot)
        self.pathmgr = PathManager(bot)
        self.map_data = None
        self.queens = None
        self.qp = None
        self.datamgr = DataManager(bot)

    def setup(self) -> None:
        """
        Setting MapData here in case we need to pass this to other managers.
        Though we could use a # function in PathManager: get_map_data, but I think this is fine

        Returns
        -------
        """
        # TODO: Choose random build here (eventually)
        self.map_data = MapData(self.bot)
        self.pathmgr.setup(self.map_data)
        self.creepmgr.setup(self.pathmgr)
        self.macromgr.setup(self.creepmgr)
        self.combatmgr.setup()

        self.datamgr.setup()  # Needs to be last

    async def manage(self, iteration: int) -> None:
        # TODO: It might be better to manage iteration calls here
        await self.macromgr.manage()
        await self.combatmgr.manage()
        if iteration % 120 == 0:
            await self.log_data()

    async def log_data(self):
        await self.datamgr.log_worker_distribution()
        await self.datamgr.log_unit_percentages(self.macromgr.build.units_to_train)







