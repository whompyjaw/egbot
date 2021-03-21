import unittest
from unittest import mock
from collections import defaultdict

from datamgr import DataManager
from eg import EGbot


class TestSc2Logger(unittest.TestCase):
    def setUp(self) -> None:
        self.logger = DataManager()
        # return super().setUp() (not sure why pylance autocompletes this)
        self.bot = EGbot()
        self.bot.game_data = mock.Mock()


    def test_log_distribution_workers(self):
        expect = defaultdict()
        expect[5] = {}
        expect[5]['min'] = 12
        expect[5]['gas1'] = 3
        expect[5]['gas2'] = 2

        self.bot.townhalls = None

        res = self.logger.worker_dirstribution(self.bot)
        assert expect == res