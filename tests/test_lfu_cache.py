# pylint: skip-file

import unittest
from unittest.mock import Mock
from collections import Counter

from src.randcache import LFUCache


class TestLFUCache(unittest.TestCase):

    def setUp(self):
        self.cache = LFUCache(capacity=6, callback=None)

        keys = [1, 2, 3, 4, 5]
        vals = [2, 3, 4, 5, 6]

        for key, value in zip(keys, vals):
            self.cache[key] = value

    def test_lfu_get_item_lfu_update(self):
        self.cache[1]
        self.cache[3]
        self.cache[5]
        self.cache[5]
        self.cache[1]
        self.cache[3]
        self.cache[2]

        k, v = self.cache.popitem()
        self.assertEqual(k, 4)

        k, v = self.cache.popitem()
        self.assertEqual(k, 2)

    def test_lfu_set_item_lfu_update(self):
        self.cache[6] = 7
        self.cache.popitem()
        self.cache.popitem()
        self.cache.popitem()
        self.cache.popitem()
        self.cache.popitem()
        
        self.assertIn(6, self.cache)
        self.assertNotIn(5, self.cache)

    def test_lfu_eviction(self):
        self.cache[6] = 7
        self.cache[1]
        self.cache[2]
        self.cache[7] = 8
        self.cache[8] = 9

        self.assertNotIn(3, self.cache)
        self.assertNotIn(4, self.cache)

    def test_lfu_callback(self):
        f = Mock()

        callback_cache = LFUCache(capacity=4, callback=f)
        
        callback_cache[6] = 7
        callback_cache[7] = 8
        callback_cache[8] = 9
        callback_cache[9] = 10
        callback_cache[10] = 11

        f.assert_called_with(6, 7)

    def test_lfu_change_item_value(self):
        self.cache[1] = 3
        self.cache[2] = 4
        self.cache[3] = 5

        self.assertIn(1, self.cache)
        self.assertIn(2, self.cache)
        self.assertIn(3, self.cache)
    
    def test_pop_from_empty_cache_raises(self):
        cache = LFUCache(capacity=6, callback=None)
        
        self.assertRaises(KeyError, lambda: cache.popitem())