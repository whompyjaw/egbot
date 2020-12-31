from sc2.ids.unit_typeid import UnitTypeId
from sc2.unit import Unit


class MacroManager:

    macro_actions = []

    def __init__(self, bot, structures):
        self.bot = bot
        self.structures = structures
        # dk why you need to typecast this as a unit
        self.hq: Unit = self.bot.townhalls.first
        # self.hq = structures.firstexpansion
        #        self.used_tumors: Set[int] = set()
        self.inject_interval = 100

    async def build_pool(self):  # Build spawning pool
        if (
            self.structures(UnitTypeId.SPAWNINGPOOL).amount
            + self.already_pending(UnitTypeId.SPAWNINGPOOL)
            == 0
        ):
            if self.can_afford(UnitTypeId.SPAWNINGPOOL):
                await self.build(
                    UnitTypeId.SPAWNINGPOOL,
                    near=self.hq.position.towards(self.bot.game_info.map_center, 5),
                )

    async def build_gas(self):
        if self.can_afford(UnitTypeId.EXTRACTOR):
            # May crash if we dont have any drones
            for hatch in self.townhalls.ready:
                for vg in self.vespene_geyser.closer_than(10, hatch):
                    if not self.worker_en_route_to_build(UnitTypeId.EXTRACTOR):
                        await self.build(UnitTypeId.EXTRACTOR, vg)
                        break

    def add_structure(self, unit):
        self.structures = unit

    def _position_blocks_expansion(self, pos):
        """
        TODO: figure out why Union and self.expansion_locations_list say they have an error yet no issues arise in the code.  Suspect Pylint is goofed.
        Note: used pos: Union[Point2, Unit] instead of just pos: Point2 in attempt to fix a y is -1, self.height is 176 error.  Seems to work...

        From Glenn: You don't need to instantiate pos in this function because you're passing a position to this function. Python already knows what it is.
                    Also, put these docstring inside the function you are referring to.
                    we should do that for future TODO's as well.
        """

        blocks_expansion = False
        for expansion in self.expansion_locations_list:
            if pos.distance_to(expansion) < 6:
                blocks_expansion = True
                break
        return blocks_expansion

    # Glenn: Idk where this belongs
    # TODO: Will need to add an array or vector of buildings for "worker_en_route_to_build" to check instead of only HATCHERY
    # TODO: Check for max number of hatcheries

    async def expand():       
        # Expands to nearest location when 300 minerals are available up to maximum 5 hatcheries
        if (
            self.townhalls.ready.amount + self.already_pending(UnitTypeId.HATCHERY)
            < 5
        ):
            if self.can_afford(UnitTypeId.HATCHERY):
                await self.expand_now()
