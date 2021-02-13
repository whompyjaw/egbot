from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units
from queens_sc2.queens import Queens


class MacroManager:
    def __init__(self, bot):
        self.bot = bot
        self.actions = []

    async def manage(self):
        await self.build_drone()
        await self.build_overlords()
        await self.build_structures()
        await self.build_queens()


    async def build_structures(self) -> None:
        await self.build_pool()
        await self.build_gas()
        await self.expand()


    async def build_pool(self) -> None:
        """Builds a Spawning Pool near starting Hatchery location"""

        hq: Unit = self.bot.townhalls.first
        pool_ready: Units = self.bot.structures(UnitTypeId.SPAWNINGPOOL).ready  # NOTE: made for fun
        pool_pending: Units = self.bot.already_pending(UnitTypeId.SPAWNINGPOOL)

        if not pool_ready and not pool_pending:
            if self.bot.can_afford(UnitTypeId.SPAWNINGPOOL):
                await self.bot.build(
                    UnitTypeId.SPAWNINGPOOL,
                    near=hq.position.towards(self.bot.game_info.map_center, 5),
                )

    async def build_gas(self) -> None:
        """
        Build Extractors at Vespene Gas locations near Hatchery. If only one
        hatch is up, build one gas, once hatches.amount > 1 then begin building gas at all locations.
        """
        iteration: int = self.bot.iteration

        if self.bot.can_afford(UnitTypeId.EXTRACTOR) and iteration > 180:
                for vg in self.bot.vespene_geyser.closer_than(10, self.bot.townhalls.ready.random):
                    if not self.bot.worker_en_route_to_build(UnitTypeId.EXTRACTOR):
                        await self.bot.build(UnitTypeId.EXTRACTOR, vg)
                        break

    async def expand(self) -> None:
        """
        Expands to nearest location when 300 minerals are available up to maximum 5 hatcheries
        Currently this doesn't account for if enemies are in the way I guess (per a note from the sc2 lib)
        """
        hatch_count = self.bot.townhalls.ready.amount

        if (hatch_count + self.bot.already_pending(UnitTypeId.HATCHERY)) < 5:
            if self.bot.can_afford(UnitTypeId.HATCHERY):
                next_expac = await self.bot.get_next_expansion()
                # TODO: Try to select drone that is pending or is in egg form (for strategy sprint)
                worker = self.bot.select_build_worker(next_expac)
                if worker:
                    worker.build(UnitTypeId.HATCHERY, next_expac)

    async def build_drone(self) -> None:
        """
        Builds drones; drone limit based on # of hatcheries; 22 drones per hatchery
        """
        drone: UnitTypeId = UnitTypeId.DRONE
        overlord: UnitTypeId = UnitTypeId.OVERLORD
        larvae: Units = self.bot.units(UnitTypeId.LARVA)

        if (
            larvae
            and self.bot.can_afford(drone)
            and (self.bot.supply_left > 1 or self.bot.already_pending(overlord)) >= 1
        ):
            if (
                self.bot.supply_workers
                - self.bot.worker_en_route_to_build(UnitTypeId.HATCHERY)
                + self.bot.already_pending(drone)
            ) < 85:
                larvae.random.train(drone)

    async def build_overlords(self) -> None:
        """
        Build overlords up to max
        """
        # TODO: Will need to figure out if we need to create more than 200 supply OLs
        larvae: Units = self.bot.units(UnitTypeId.LARVA)
        overlord: UnitTypeId = UnitTypeId.OVERLORD

        if self.bot.supply_used <= 13 and self.bot.already_pending(overlord) < 1:
            larvae.random.train(overlord)
        elif (
            self.bot.supply_cap > 14
            and self.bot.supply_left < 3 # TODO: 2 or 3?
            and larvae
            and self.bot.can_afford(overlord)
            and self.bot.already_pending(overlord) < 2
        ):
            larvae.random.train(overlord)

    async def build_queens(self) -> None:
        """
        If a pool exists and bot can afford build a queen.

        :params: Queens object
        """
        queen_count: int = self.bot.units(UnitTypeId.QUEEN).amount
        queens: Queens = self.bot.queens
        #hatches = dictops.get_values(self.structures, 'Hatchery')
        
        cq: int = queens.policies.get('creep_policy').max_queens
        dq: int = queens.policies.get('defence_policy').max_queens
        iq: int = queens.policies.get('inject_policy').max_queens

        if (queen_count + self.bot.already_pending(UnitTypeId.QUEEN)) < (cq+dq+iq):
            if self.bot.structures(UnitTypeId.SPAWNINGPOOL).ready:
                if self.bot.can_afford(UnitTypeId.QUEEN):
                    for hatchery in self.bot.townhalls.ready:
                        if hatchery.is_idle:
                            hatchery.train(UnitTypeId.QUEEN)


    # async def _get_rdy_struct(self, id: UnitTypeId) -> Units:
    #     return self.bot.structures(id).ready 