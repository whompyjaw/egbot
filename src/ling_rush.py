from sc2.unit import Unit
from sc2.units import Units


class LingRush:
    """Reference: https://github.com/DrInfy/sharpy-sc2/tree/develop/dummies/zerg"""

    def __init__(self):
        pass

    async def opening_strats(self):
        """
        Starter method to develop strategies for various openings.  Uses a dictionary with different strategies
        to select from.  A random number is generated when the program starts determining the strategy.
        """
        # TODO: This is already declared up top and assigned to self.hq. Do we need both?
        hq: Unit = self.townhalls.first
        strat_dict = {"pool_first": 1, "expand_first": 2, "double_expand": 3}

    def set_strat(self):
        pass

    def strat(self):
        return self.strat

        # normal strat - let it play out
        if self.hatch_strat == strat_dict.get("pool_first"):
            await build_pool()
            if (
                self.already_pending(UnitTypeId.SPAWNINGPOOL) == 1
                and self.structures(UnitTypeId.EXTRACTOR).amount < 1
            ):
                await build_gas()
            await expand()
            if (
                self.townhalls.ready.amount == 2
                and self.structures(UnitTypeId.EXTRACTOR).amount < 3
            ):
                await build_gas()

        if self.hatch_strat == strat_dict.get("expand_first"):
            # expand as long as less than 2 hatcheries
            if (
                self.townhalls.ready.amount + self.already_pending(UnitTypeId.HATCHERY)
                < 2
            ):
                await expand()
            # elif to see if pool AND 2 hatcheries built, if so expand
            elif (
                self.structures(UnitTypeId.SPAWNINGPOOL).amount
                + self.already_pending(UnitTypeId.SPAWNINGPOOL)
                == 1
                and self.townhalls.ready.amount
                + self.already_pending(UnitTypeId.HATCHERY)
                == 2
            ):
                await expand()
            # if and elif are false, build pool
            else:
                await build_pool()
            # build a gas if pool is pending
            if (
                self.already_pending(UnitTypeId.SPAWNINGPOOL) == 1
                and self.structures(UnitTypeId.EXTRACTOR).amount < 1
            ):
                await build_gas()
            if (
                self.townhalls.ready.amount == 2
                and self.structures(UnitTypeId.EXTRACTOR).amount < 3
            ):
                await build_gas()

        if self.hatch_strat == strat_dict.get("double_expand"):
            # expand as long as less than 2 hatcheries
            if (
                self.townhalls.ready.amount + self.already_pending(UnitTypeId.HATCHERY)
                < 3
            ):
                await expand()
            # if pool built AND 3 hatcheries, continue to attempt to expand
            elif (
                self.structures(UnitTypeId.SPAWNINGPOOL).amount
                + self.already_pending(UnitTypeId.SPAWNINGPOOL)
                == 1
                and self.townhalls.ready.amount
                + self.already_pending(UnitTypeId.HATCHERY)
                == 3
            ):
                await expand()
            # if no pool built yet and 3 hatcheries pending or built, build pool
            else:
                await build_pool()

            # build a gas if pool is pending
            if (
                self.already_pending(UnitTypeId.SPAWNINGPOOL) == 1
                and self.structures(UnitTypeId.EXTRACTOR).amount < 1
            ):
                await build_gas()
            if (
                self.townhalls.ready.amount == 3
                and self.structures(UnitTypeId.EXTRACTOR).amount < 3
            ):
                await build_gas()
