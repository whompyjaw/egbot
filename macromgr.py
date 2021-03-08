from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.unit import Unit
from sc2.units import Units
from sc2.unit import UpgradeId


class MacroManager:
    def __init__(self, bot):
        self.bot = bot
        self.actions = []
        self.roach_hydra = False
        self.zergling: UnitTypeId = UnitTypeId.ZERGLING
        self.ling_speed = UpgradeId.ZERGLINGMOVEMENTSPEED
        self.hq = None

    def setup(self):
        self.hq: Unit = self.bot.townhalls.first

    async def manage(self):
        if (self.bot.units(UnitTypeId.DRONE).amount <= (self.bot.townhalls.ready.amount*19))\
                and self.bot.units(UnitTypeId.DRONE).amount <= 85:
            await self.build_drone()
        await self.build_overlords()
        await self.build_structures()
        if self.bot.units(UnitTypeId.DRONE).amount >= 16 and self.bot.units(UnitTypeId.ZERGLING).amount <= 15:
            await self.build_zerglings()
        #await self.build_roaches()
        await self.build_hydras()
        if self.bot.already_pending_upgrade(self.ling_speed) == 0:
            await self.upgrade_ling_speed()
        if self.bot.structures(UnitTypeId.HYDRALISKDEN).ready:
            await self.upgrade_hydralisks()
        if self.bot.structures(UnitTypeId.EVOLUTIONCHAMBER).ready:
            await self.upgrade_units()
        if self.bot.iteration % 16 == 0:
            await self.bot.distribute_workers()


    async def build_structures(self) -> None:
        if self.bot.townhalls.amount >= 2:
            if self.bot.structures(UnitTypeId.EXTRACTOR).amount < 1:
                await self.build_gas()
            await self.build_pool()
        # if self.bot.structures(UnitTypeId.SPAWNINGPOOL).ready:
        #     if self.bot.structures(UnitTypeId.EXTRACTOR).amount < 2:
        #         await self.build_gas()
            #await self.build_roach_warren()
            await self.morph_lair()
        if self.bot.structures(UnitTypeId.LAIR).ready:
            if self.bot.structures(UnitTypeId.EXTRACTOR).amount < 3:
                await self.build_gas()
            await self.build_hydra_den()
        if self.bot.supply_used >= 17 and self.bot.townhalls.amount < 3:
            await self.expand()
        if self.bot.supply_used >= 90:
            await self.expand()
        if self.bot.townhalls.ready.amount >= 2:
            await self.build_evo_chamber()
        if self.bot.townhalls.ready.amount >= 5:
            await self.build_gas()

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

    async def build_hydra_den(self):
        hydra_den_id = UnitTypeId.HYDRALISKDEN
        hydra_den: Units = self.bot.structures(UnitTypeId.HYDRALISKDEN)

        if not hydra_den.ready and not self.bot.already_pending(hydra_den_id):
            if self.bot.can_afford(hydra_den_id):
                await self.bot.build(
                    UnitTypeId.HYDRALISKDEN,
                    near=self.bot.main_base_ramp.bottom_center.towards(self.bot.game_info.map_center, 3),
                )

    async def build_evo_chamber(self):
        evo_id = UnitTypeId.EVOLUTIONCHAMBER
        evo_chamber: Units = self.bot.structures(UnitTypeId.EVOLUTIONCHAMBER)

        if evo_chamber.amount < 2 and not self.bot.already_pending(evo_id):
            if self.bot.can_afford(evo_id):
                await self.bot.build(
                    UnitTypeId.EVOLUTIONCHAMBER,
                    near=self.bot.townhalls[1].position.towards(self.bot.game_info.map_center, 5),
                )

    async def build_gas(self) -> None:
        """
        Build Extractors at Vespene Gas locations near Hatchery. If only one
        hatch is up, build one gas, once hatches.amount > 1 then begin building gas at all locations.
        """
        #iteration: int = self.bot.iteration

        if self.bot.can_afford(UnitTypeId.EXTRACTOR):# and iteration > 180:
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

    async def morph_lair(self):
        if self.hq.is_idle and not self.bot.townhalls(UnitTypeId.LAIR):
            if self.bot.can_afford(UnitTypeId.LAIR):
                self.hq.build(UnitTypeId.LAIR)

    async def build_drone(self) -> None:
        """
        Builds drones; drone limit based on # of hatcheries; 22 drones per hatchery
        """
        drone: UnitTypeId = UnitTypeId.DRONE
        overlord: UnitTypeId = UnitTypeId.OVERLORD
        #hatcheries: Units = self.bot.townhalls.ready.amount
        larvae: Units = self.bot.units(UnitTypeId.LARVA)

        #if self.bot.units(drone).amount <= hatcheries*22:
        if self.bot.can_afford(drone) and larvae\
                and (self.bot.supply_left > 2 or self.bot.already_pending(overlord)) >= 1:
            larvae.random.train(drone)

        # if (
        #         larvae
        #         and self.bot.can_afford(drone)
        #         and (self.bot.supply_left > 1 or self.bot.already_pending(overlord)) >= 1
        # ):
        #     if (
        #             self.bot.supply_workers
        #             - self.bot.worker_en_route_to_build(UnitTypeId.HATCHERY)
        #             + self.bot.already_pending(drone)
        #     ) < 85:
        #         larvae.random.train(drone)

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
                and self.bot.already_pending(overlord) < 3
        ):
            larvae.random.train(overlord)

    async def build_zerglings(self):

        pool_ready: Units = self.bot.structures(UnitTypeId.SPAWNINGPOOL).ready
        larvae: Units = self.bot.units(UnitTypeId.LARVA)

        if pool_ready and self.bot.can_afford(self.zergling) and larvae and self.bot.supply_left > 2:
            larvae.random.train(self.zergling)

    async def build_roaches(self):
        roach_warren_ready: Units = self.bot.structures(UnitTypeId.ROACHWARREN).ready
        roach: Unit = UnitTypeId.ROACH
        larvae: Units = self.bot.units(UnitTypeId.LARVA)

        if roach_warren_ready and self.bot.can_afford(roach) and larvae and self.bot.supply_left > 2:
            larvae.random.train(roach)

    async def build_hydras(self):
        hydra_den_ready: Units = self.bot.structures(UnitTypeId.HYDRALISKDEN).ready
        hydra: Unit = UnitTypeId.HYDRALISK
        larvae: Units = self.bot.units(UnitTypeId.LARVA)

        if hydra_den_ready and self.bot.can_afford(hydra) and larvae and self.bot.supply_left > 2:
            larvae.random.train(hydra)

    async def upgrade_ling_speed(self):
        pool: Units = self.bot.structures(UnitTypeId.SPAWNINGPOOL)
        if pool.ready and self.bot.can_afford(self.ling_speed) and not self.bot.already_pending_upgrade(
                self.ling_speed):
            self.bot.research(self.ling_speed)

    async def upgrade_hydralisks(self):
        hydra_den: Units = self.bot.structures(UnitTypeId.HYDRALISKDEN)

        if self.bot.already_pending_upgrade(UpgradeId.EVOLVEGROOVEDSPINES) == 0\
                and self.bot.can_afford(UpgradeId.EVOLVEGROOVEDSPINES):
            self.bot.research(UpgradeId.EVOLVEGROOVEDSPINES)

        elif self.bot.already_pending_upgrade(UpgradeId.EVOLVEMUSCULARAUGMENTS) == 0\
                and self.bot.can_afford(UpgradeId.EVOLVEMUSCULARAUGMENTS):
            self.bot.research(UpgradeId.EVOLVEMUSCULARAUGMENTS)


    async def upgrade_units(self):
        evo_chambers: Units = self.bot.structures(UnitTypeId.EVOLUTIONCHAMBER).ready

        targetUpgrades = [AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL1, AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL1,
                           AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL1, AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL2,
                           AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL2, AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL2,
                           AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL3, AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL3,
                           AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL3]

        avail_upgrades = await self.bot.get_available_abilities(evo_chambers, ignore_resource_requirements=True)

        for i, upgrades in enumerate(avail_upgrades):
            evo = evo_chambers[i]
            for upgrade in targetUpgrades:
                if upgrade in upgrades:
                    if self.bot.can_afford(upgrade) and evo.is_idle:
                        self.bot.do(evo(upgrade))
                        break

