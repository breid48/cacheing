# pylint: skip-file

import unittest
from unittest.mock import Mock

from src.rcache import RandomCache


class TestRandomCache(unittest.TestCase):

    def setUp(self):
        self.cache = RandomCache(capacity=6, callback=None)

        keys = [1, 2, 3, 4, 5]
        vals = [2, 3, 4, 5, 6]

        for key, value in zip(keys, vals):
            self.cache[key] = value

    def test_cache_length(self):
        self.assertEqual(5, len(self.cache))

        self.cache[1]
        self.cache[2]
        self.cache[3] = 5
        self.cache[3] = 6
        self.assertEqual(5, len(self.cache))

        del self.cache[1]
        self.assertEqual(4, len(self.cache))

        self.cache.popitem()
        self.assertEqual(3, len(self.cache))

    def test_random_eviction(self):
        self.cache[6] = 7
        self.cache[7] = 8
        self.cache[8] = 9
 
        self.assertEqual(len(self.cache), 6)

    def test_callback(self):
        f = Mock()

        callback_cache = RandomCache(capacity=4, callback=f)
        
        callback_cache[6] = 7
        callback_cache[7] = 8
        callback_cache[8] = 9
        callback_cache[9] = 10
        callback_cache[10] = 11

        f.assert_called()

    def test_change_item_value(self):
        self.cache[1] = 3
        self.cache[2] = 4
        self.cache[3] = 5
        self.cache[4] = 6
        self.cache[5] = 7
        self.cache[6] = 8

        self.assertIn(1, self.cache)
        self.assertIn(2, self.cache)
        self.assertIn(3, self.cache)
        self.assertIn(4, self.cache)
        self.assertIn(5, self.cache)
        self.assertIn(6, self.cache)