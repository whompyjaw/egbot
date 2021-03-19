from sc2.ids.unit_typeid import UnitTypeId
from sc2.ids.ability_id import AbilityId
from sc2.unit import Unit
from sc2.units import Units
from sc2.unit import UpgradeId
from constants import *
import random
from typing import List
from queens_sc2.queens import Queens
from queen_policy import QueenPolicy


class MacroManager:
    def __init__(self, bot):
        self.bot = bot
        self.actions = []
        self.roach_hydra = False
        self.zergling: UnitTypeId = UnitTypeId.ZERGLING
        self.ling_speed = UpgradeId.ZERGLINGMOVEMENTSPEED
        self.hq = None
        self.target_upgrades = []
        self.build = None
        self.queens = None
        self.qp = None
        self.creepmgr = None

    def setup(self, build, creepmgr):
        self.hq: Unit = self.bot.townhalls.first
        self.target_upgrades = [AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL1, AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL1,
                                AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL1, AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL2,
                                AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL2, AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL2,
                                AbilityId.RESEARCH_ZERGMISSILEWEAPONSLEVEL3, AbilityId.RESEARCH_ZERGGROUNDARMORLEVEL3,
                                AbilityId.RESEARCH_ZERGMELEEWEAPONSLEVEL3]

        self.build = build
        self.qp = QueenPolicy(self.bot)
        self.queens = Queens(self.bot, True, self.qp.queen_policy)
        self.creepmgr = creepmgr

    async def manage(self):
        await self.build_structures()
        await self.train_units()
        # TODO: Not sure if better since we'll have to get all the "ready" structures. We can keep a running list of
        # ready structures, and if a building is destroyed, we remove it from that list. This could work for if we use
        # a build list in our policy/config.
        await self.upgrade_units()

        if self.bot.iteration % 16 == 0:
            await self.bot.distribute_workers()

        if self.bot.iteration % 90 == 0 and self.bot.units(UnitTypeId.QUEEN):
            targets = self.creepmgr.get_creep_targets()
            if targets:
                self.queens.update_creep_targets(targets)
        await self.queens.manage_queens(self.bot.iteration)

    async def train_units(self):
        # get supply?
        await self.train_overlords()
        units: dict = self.build.units_to_train
        larvae: Units = self.bot.units(UnitTypeId.LARVA)
        weights: List[float] = []
        trainable_units: List[UnitTypeId] = []

        # unit = UnitTypeId
        for unit in units:
            unit_attrs: dict = units.get(unit)
            struct = self.bot.structures(unit_attrs.get(STRUCTURE))  # get structure status
            if struct.ready:
                unit_count = self.bot.units(unit).amount + self.bot.already_pending(unit)
                unit_distr = unit_count * unit_attrs.get(SUPPLY_COST) / 200
                if unit == UnitTypeId.QUEEN:
                    if unit_distr <= unit_attrs.get(WEIGHT):
                        await self.build_queens()
                if unit_distr <= unit_attrs.get(WEIGHT):
                    weights.append(unit_attrs.get(WEIGHT))
                    trainable_units.append(unit)

        if trainable_units:
            units_to_train = random.choices(trainable_units, weights, k=larvae.amount)
            for unit in units_to_train:
                if larvae and self.bot.supply_left > 2:
                    larvae.random.train(unit, can_afford_check=True)

    async def build_queens(self) -> None:
        """
        If a pool exists and bot can afford build a queen.

        :params: Queens object
        """
        queen_count: int = self.bot.units(UnitTypeId.QUEEN).amount
        queens: Queens = self.queens

        # TODO: Probably want to keep this in case we update the queen count in the policy.
        cq: int = queens.policies.get('creep_policy').max_queens
        dq: int = queens.policies.get('defence_policy').max_queens
        iq: int = queens.policies.get('inject_policy').max_queens

        if (queen_count + self.bot.already_pending(UnitTypeId.QUEEN)) < (cq + dq + iq):
            if self.bot.structures(UnitTypeId.SPAWNINGPOOL).ready:
                if self.bot.can_afford(UnitTypeId.QUEEN):
                    for hatchery in self.bot.townhalls.ready:
                        if hatchery.is_idle:
                            hatchery.train(UnitTypeId.QUEEN)


    async def build_structures(self) -> None:
        await self.build_unit_structures()

        # drone_amt = self.bot.units(UnitTypeId.DRONE).amount
        # if drone_amt % self.build.expand_rate == 0 or self.can_expand is True:
        #     self.can_expand = True
        #     await self.expand()

        if self.bot.townhalls.amount >= 2:
            if self.bot.structures(UnitTypeId.EXTRACTOR).amount < 1:
                await self.build_gas()
        if self.bot.structures(UnitTypeId.LAIR).ready:
            if self.bot.structures(UnitTypeId.EXTRACTOR).amount < 3:
                await self.build_gas()
        # TODO: What if we use a modulo? Like expand every 17-20 supply or something.
        # # 2nd expac
        # if self.bot.supply_used >= self.build.expand_rate and self.bot.townhalls.amount == 1:
        #     await self.expand()
        # # 3rd expac
        # if self.bot.supply_used >= self.build.expand_rate * 1.875 and self.bot.townhalls.amount == 2:
        #     await self.expand()
        # # 4th expac
        # if self.bot.supply_used >= self.build.expand_rate * 3:
        #     await self.expand()
        if self.bot.townhalls.ready.amount >= 2:
            await self.build_evo_chamber()
        if self.bot.townhalls.ready.amount >= 5:
            await self.build_gas()

    async def build_unit_structures(self):
        structs: List[UnitTypeId] = self.build.build_sequence.items()
        await self._check_expand()

        for struct, attributes in structs:
            if struct is not UnitTypeId.HATCHERY:
                if self.bot.supply_used >= attributes.get(SUPPLY) and not self.bot.structures(struct) and not self.bot.already_pending(struct):
                    if self.bot.can_afford(struct):
                        if struct == UnitTypeId.LAIR:
                            self.hq.build(struct)
                        elif struct == UnitTypeId.SPAWNINGPOOL:
                            if not attributes.get(BEFORE_HATCH):
                                if self.bot.townhalls.amount >= 2:
                                    await self._build_structure(struct, attributes.get(LOCATION))

                        else:
                            await self._build_structure(struct, attributes.get(LOCATION))

    async def _build_structure(self, id, location):
        worker = self.bot.select_build_worker(location)
        if worker:
            worker.build(id, location)

    async def _check_expand(self):
        hatcheries = self.build.build_sequence.get(id.HATCHERY).values()
        for hatch in hatcheries:
            if hatch.get(SUPPLY) <= self.bot.supply_used and hatch.get(
                    TOWNHALL_REQUIREMENT) >= self.bot.townhalls.amount:
                await self.expand()

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

        if evo_chambers:
            avail_upgrades = await self.bot.get_available_abilities(evo_chambers, ignore_resource_requirements=True)
            for chamber, upgrades in enumerate(avail_upgrades):
                evo = evo_chambers[chamber]
                for upgrade in self.target_upgrades:
                    if upgrade in upgrades:
                        if self.bot.can_afford(upgrade) and evo.is_idle:
                            self.bot.do(evo(upgrade))
                            break

        if self.bot.already_pending_upgrade(self.ling_speed) == 0:
            await self.upgrade_ling_speed()
        if self.bot.structures(UnitTypeId.HYDRALISKDEN).ready:
            await self.upgrade_hydralisks()

