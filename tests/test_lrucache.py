import unittest

from collections import OrderedDict

from src.randcache import LRUCache


class TestLRUCache(unittest.TestCase):

    def setUp(self):
        self.cache = LRUCache(capacity=6, callback=None)

        keys = [1, 2, 3, 4, 5]
        vals = [2, 3, 4, 5, 6]

        for key, value in zip(keys, vals):
            self.cache[key] = value

    def test_lru_cache_constructor(self):
        self.assertIsInstance(self.cache, OrderedDict)