from typing import List
from sc2.unit import UnitTypeId as UnitID
from sc2.position import Point2


class QueenPolicy:

  def __init__(self, bot, paths: List[Point2]):
    self.bot = bot
    self.paths = paths

  def get_policy(self) -> dict:
      queen_policy: dict = {
        "creep_queens": {
            "active": True,
            "max": 2,
            "priority": True,
            "defend_against_air": True,
            "defend_against_ground": False,
            "distance_between_existing_tumors": 10,
            # "should_tumors_block_expansions": False,
            # "creep_targets": self.paths,
          #   "spread_style": str, # "targeted" is default, or "random"
          #   "rally_point": Point2,
            "first_tumor_position": self.bot.start_location.towards(
                          self.bot.main_base_ramp.top_center, 11
                      ),
          #   "prioritize_creep": Callable, # prioritize over defending bases if energy is available?
          #   "pass_own_threats": bool, # if set to True, library wont calculate enemy near bases, you should pass air and ground threats to manage_queens() method
          #   "priority_defence_list": {
          #                 UnitID.BATTLECRUISER,
          #                 UnitID.LIBERATOR,
          #                 UnitID.LIBERATORAG,
          #                 UnitID.VOIDRAY,
          #             }, # queens will prioritise defending these unit types over all other jobs
        },
        "defence_queens": {
            "active": True,
            "max": 4,
            "priority": True,
            "defend_against_air": True,
            "defend_against_ground": True,
          # #   "attack_condition": Callable,
          # #   "attack_target": Point2,
          # #   "rally_point": Point2,
          # #   "pass_own_threats": bool,
          #   "priority_defence_list": {
          #                 UnitID.BATTLECRUISER,
          #                 UnitID.LIBERATOR,
          #                 UnitID.LIBERATORAG,
          #                 UnitID.VOIDRAY,
          #             },
        },
        "inject_queens": {
            "active": True,
            "max": 4,
            "priority": False,
            "defend_against_air": True,
            "defend_against_ground": True,
          #   "pass_own_threats": bool,
          #   "priority_defence_list": {
          #                 UnitID.BATTLECRUISER,
          #                 UnitID.LIBERATOR,
          #                 UnitID.LIBERATORAG,
          #                 UnitID.VOIDRAY,
          #             },
          },
      }
      return queen_policy