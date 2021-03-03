from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit
from sc2.units import Units
from sc2.unit import UpgradeId
from build_policy import BuildPolicy
from build_policies import *
from build_policy_consts import *


class MacroManager:
    def __init__(self, bot):
        self.bot = bot
        self.actions = []
        self.roach_hydra = False
        self.zergling: UnitTypeId = UnitTypeId.ZERGLING
        self.ling_speed = UpgradeId.ZERGLINGMOVEMENTSPEED
        self.hq = None
        self.build_policy = None

    def setup(self):
        self.hq: Unit = self.bot.townhalls.first
        self.build_policy = BuildPolicy(default)

    async def manage(self):
        await self.build_drone()
        await self.build_overlords()
        await self.build_structures()
        await self.build_zerglings()
        await self.build_roaches()
        if self.bot.already_pending_upgrade(self.ling_speed) == 0:
            await self.upgrade_ling_speed()
        if self.bot.iteration % 16 == 0:
            await self.bot.distribute_workers()
        await self.update_build_policy()
        await self.build()

    async def build_structures(self) -> None:
        await self.build_pool()
        if self.bot.structures(UnitTypeId.SPAWNINGPOOL).ready:
            await self.build_roach_warren()
            await self.build_lair()
        await self.build_gas()
        await self.expand()

    async def build_pool(self) -> None:
        """Builds a Spawning Pool near starting Hatchery location"""
        pool: Units = self.bot.structures(UnitTypeId.SPAWNINGPOOL)  # NOTE: made for fun
        pool_pending = self.bot.already_pending(UnitTypeId.SPAWNINGPOOL)

        if not pool.ready and not pool_pending:
            if self.bot.can_afford(UnitTypeId.SPAWNINGPOOL):
                await self.bot.build(
                    UnitTypeId.SPAWNINGPOOL,
                    near=self.hq.position.towards(self.bot.game_info.map_center, 5),
                )

    async def build_roach_warren(self):
        roach_warren_id = UnitTypeId.ROACHWARREN
        roach_warren: Units = self.bot.structures(UnitTypeId.ROACHWARREN)

        if not roach_warren.ready and not self.bot.already_pending(roach_warren_id):
            if self.bot.can_afford(roach_warren_id):
                await self.bot.build(
                    UnitTypeId.ROACHWARREN,
                    near=self.hq.position.towards(self.bot.game_info.map_center, 5),
                )

    # async def build_hydra_den(self):
    #     hydra_den_id = UnitTypeId.HYDRALISKDEN
    #     hydra_den: Units = self.bot.structures(UnitTypeId.HYDRALISKDEN)
    #
    #     if not hydra_den.ready and not self.bot.already_pending(hydra_den_id):
    #         if self.bot.can_afford(roach_warren_id):
    #             await self.bot.build(
    #                 UnitTypeId.ROACHWARREN,
    #                 near=self.hq.position.towards(self.bot.game_info.map_center, 5),
    #             )

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

    async def build_lair(self) -> None:
        if self.hq.is_idle and not self.bot.townhalls(UnitTypeId.LAIR):
            if self.bot.can_afford(UnitTypeId.LAIR):
                self.hq.build(UnitTypeId.LAIR)

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
                and self.bot.supply_left < 3  # TODO: 2 or 3?
                and larvae
                and self.bot.can_afford(overlord)
                and self.bot.already_pending(overlord) < 2
        ):
            larvae.random.train(overlord)

    async def build_zerglings(self):
        pool_ready: Units = self.bot.structures(UnitTypeId.SPAWNINGPOOL).ready
        larvae: Units = self.bot.units(UnitTypeId.LARVA)

        if pool_ready and self.bot.can_afford(self.zergling) and larvae and self.bot.supply_left >= 1:
            larvae.random.train(self.zergling)

    async def build_roaches(self):
        roach_warren_ready: Units = self.bot.structures(UnitTypeId.ROACHWARREN).ready
        roach = UnitTypeId.ROACH
        larvae: Units = self.bot.units(UnitTypeId.LARVA)

        if roach_warren_ready and self.bot.can_afford(roach) and larvae and self.bot.supply_left > 1:
            larvae.random.train(roach)

    async def build_hydras(self):
        pass

    async def update_build_policy(self):
        new_policy = {}
        # get enemy info from ScoutManager
        # update build policy accordingly
        self.build_policy.update(new_policy)

    async def check_upgrades(self):
        await self.upgrade_ling_speed()
        if self.build_policy.policy[UPGRADE_ARMOR]:
            #  upgrade bane speed
            pass
        if self.build_policy.policy[UPGRADE_ATTACK]:
            # upgrade attack
            pass

    async def upgrade_ling_speed(self):
        pool: Units = self.bot.structures(UnitTypeId.SPAWNINGPOOL)
        if pool.ready and self.bot.can_afford(self.ling_speed) and not self.bot.already_pending_upgrade(
                self.ling_speed):
            self.bot.research(self.ling_speed)
