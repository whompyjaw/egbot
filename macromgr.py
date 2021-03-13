from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
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
        self.target_upgrades = []
        self.build_policy = None

    def setup(self):
        self.hq: Unit = self.bot.townhalls.first
        self.target_upgrades = [AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL1, AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL1,
                                AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL1, AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL2,
                                AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL2, AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL2,
                                AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL3, AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL3,
                                AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL3]


    def setup(self):
        self.hq: Unit = self.bot.townhalls.first
        self.build_policy = BuildPolicy(default)

    async def manage(self):
        if (self.bot.units(UnitTypeId.DRONE).amount <= (self.bot.townhalls.ready.amount * 19)) \
                and self.bot.units(UnitTypeId.DRONE).amount <= 85:
            await self.train_drone()
        await self.train_overlords()
        await self.build_structures()
        if self.bot.units(UnitTypeId.DRONE).amount >= 16 and self.bot.units(UnitTypeId.ZERGLING).amount <= 15:
            await self.train_zerglings()
        # await self.train_roaches()
        await self.train_hydras()
        await self.train_units()


    async def train_units(self):

        train units
            check den
                train hydra
            check warren

        units to build:
            lings : UnitTypeId.Spawningpool,
            hydra : den,

        if key == ling
            train army unit(ling.items)
        if dict['pool']:
            build dict['lings']

            for unit in units to build:






        # TODO: Not sure if better since we'll have to get all the "ready" structures. We can keep a running list of
        # ready structures, and if a building is destroyed, we remove it from that list. This could work for if we use
        # a build list in our policy/config.
        await self.train_army_unit()
        if self.bot.already_pending_upgrade(self.ling_speed) == 0:
            await self.upgrade_ling_speed()
        if self.bot.structures(UnitTypeId.HYDRALISKDEN).ready:
            await self.upgrade_hydralisks()
        if self.bot.structures(UnitTypeId.EVOLUTIONCHAMBER).ready:
            await self.upgrade_units()
        if self.bot.iteration % 16 == 0:
            await self.bot.distribute_workers()
        await self.update_build_policy()
        await self.build()




    async def build_structures(self) -> None:
        if self.bot.townhalls.amount >= 2:
            if self.bot.structures(UnitTypeId.EXTRACTOR).amount < 1:
                await self.build_gas()
            await self.build_pool()
            # if self.bot.structures(UnitTypeId.SPAWNINGPOOL).ready:
            #     if self.bot.structures(UnitTypeId.EXTRACTOR).amount < 2:
            #         await self.build_gas()
            # await self.build_roach_warren()
            await self.morph_lair()
        if self.bot.structures(UnitTypeId.LAIR).ready:
            if self.bot.structures(UnitTypeId.EXTRACTOR).amount < 3:
                await self.build_gas()
            await self.build_hydra_den()
        # TODO: What if we use a modulo? Like expand every 17-20 supply or something.
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
        # iteration: int = self.bot.iteration

        if self.bot.can_afford(UnitTypeId.EXTRACTOR):  # and iteration > 180:
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

    async def train_drone(self) -> None:
        """
        Builds drones; drone limit based on # of hatcheries; 22 drones per hatchery
        """
        drone: UnitTypeId = UnitTypeId.DRONE
        overlord: UnitTypeId = UnitTypeId.OVERLORD
        # hatcheries: Units = self.bot.townhalls.ready.amount
        larvae: Units = self.bot.units(UnitTypeId.LARVA)

        # if self.bot.units(drone).amount <= hatcheries*22:
        if larvae and self.bot.can_afford(drone) and (
                self.bot.supply_left > 2 or self.bot.already_pending(overlord)) >= 1:
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

    async def train_overlords(self) -> None:
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

    async def train_army_unit(self, structure: Units, unit_id: UnitTypeId, larvae: Units):
        # TODO: How can we use one function to build any type of unit based on conditions?
        # All units have a building, larva, and cost requirement/condition
        # Don't have to do this, but maybe get the brain thinking how we can dry our code
        # This opens doors to going by config/policy
        # Could also do `train_unit` to pass in drone or overlord, but maybe too many special conditions.
        if structure.ready and self.bot.can_afford(unit_id) and larvae and self.bot.supply_left > 2:
            larvae.random.train(unit_id)

        # We could then have more special conditions if needed for unique units.
        if unit_id == UnitTypeId.INFESTOR:
            # check special conditions, not sure if we will need this, but expanding the idea.
            pass

    async def execute_build(self, s **kwargs):
        # not sure... Somehow i think we can create a function based on kwargs, which would be parsed from the config
        pass

    async def build_structure(self, sequence: list):
        # TODO: How can we pass in a sequence of a build to execute over time?
        # We don't have to do this, but maybe get the brain thinking how we can DRY our code
        pass

    async def upgrade_ability(self, structure: Unit, ability: AbilityId):
        # TODO: Same concept as others
        pass

    async def build_zerg(self):
        pool_ready: Units = self.bot.structures(UnitTypeId.SPAWNINGPOOL).ready
        larvae: Units = self.bot.units(UnitTypeId.LARVA)

        if pool_ready and self.bot.can_afford(self.zergling) and larvae and self.bot.supply_left > 2:
            larvae.random.train(self.zergling)

    async def train_roaches(self):
        roach_warren_ready: Units = self.bot.structures(UnitTypeId.ROACHWARREN).ready
        roach = UnitTypeId.ROACH
        larvae: Units = self.bot.units(UnitTypeId.LARVA)

        if roach_warren_ready and self.bot.can_afford(roach) and larvae and self.bot.supply_left > 2:
            larvae.random.train(roach)

    async def train_hydras(self):
        hydra_den_ready: Units = self.bot.structures(UnitTypeId.HYDRALISKDEN).ready
        hydra: Unit = UnitTypeId.HYDRALISK
        larvae: Units = self.bot.units(UnitTypeId.LARVA)

        if hydra_den_ready and self.bot.can_afford(hydra) and larvae and self.bot.supply_left > 2:
            larvae.random.train(hydra)

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

    async def upgrade_hydralisks(self):
        hydra_den: Units = self.bot.structures(UnitTypeId.HYDRALISKDEN)

        if self.bot.already_pending_upgrade(UpgradeId.EVOLVEGROOVEDSPINES) == 0 \
                and self.bot.can_afford(UpgradeId.EVOLVEGROOVEDSPINES):
            self.bot.research(UpgradeId.EVOLVEGROOVEDSPINES)

        elif self.bot.already_pending_upgrade(UpgradeId.EVOLVEMUSCULARAUGMENTS) == 0 \
                and self.bot.can_afford(UpgradeId.EVOLVEMUSCULARAUGMENTS):
            self.bot.research(UpgradeId.EVOLVEMUSCULARAUGMENTS)

    async def upgrade_units(self):
        evo_chambers: Units = self.bot.structures(UnitTypeId.EVOLUTIONCHAMBER).ready
        avail_upgrades = await self.bot.get_available_abilities(evo_chambers, ignore_resource_requirements=True)

        for chamber, upgrades in enumerate(avail_upgrades):
            evo = evo_chambers[chamber]
            for upgrade in self.target_upgrades:
                if upgrade in upgrades:
                    if self.bot.can_afford(upgrade) and evo.is_idle:
                        self.bot.do(evo(upgrade))
                        break
