# pylint: skip-file

import unittest
from unittest.mock import Mock

from src.rcache import VolatileLFUCache


class TestVolatileLFUCache(unittest.TestCase):

    def setUp(self):
        self.cache = VolatileLFUCache(capacity=6, callback=None)

        self.cache[1, True] = 2
        self.cache[2, True] = 3
        self.cache[3, True] = 4
        self.cache[4, True] = 5
        self.cache[5, True] = 6

    def test_get_item_lfu_update(self):

        self.cache[1]
        key, value = self.cache.popitem()
        self.assertEqual(key, 2)

        self.cache[3]
        self.cache[4]
        self.cache[5]
        key, value = self.cache.popitem()
        self.assertEqual(key, 1)
    
    def test_get_item_lfu_update_with_persistent_keys(self):
        cache = VolatileLFUCache(capacity=6, callback=None)

        cache[1, True] = 2
        cache[2, False] = 3
        cache[3, True] = 4
        cache[4, True] = 5
        cache[5, True] = 6

        cache[1]
        key, value = cache.popitem()
        self.assertEqual(key, 3)

        cache[4]
        cache[5]
        k, v = cache.popitem()
        self.assertEqual(k, 1)

    def test_lfu_set_item_lfu_update(self):
        self.cache[6, True] = 7
        self.cache.popitem()
        self.cache.popitem()
        self.cache.popitem()
        self.cache.popitem()
        self.cache.popitem()

        self.assertIn(6, self.cache)
        
        self.assertNotIn(1, self.cache)
        self.assertNotIn(2, self.cache)
        self.assertNotIn(3, self.cache)
        self.assertNotIn(4, self.cache)
        self.assertNotIn(5, self.cache)
    
    def test_lfu_set_item_with_persistence(self):
        cache = VolatileLFUCache(capacity=5)

        cache[1, False] = 2
        cache[2, False] = 3
        cache[3, False] = 4
        cache[4, False] = 5
        cache[5, False] = 6

        cache[6, False] = 7
        cache[7, False] = 8
        cache[8, False] = 9

        self.assertIn(1, cache)
        self.assertIn(2, cache)
        self.assertIn(3, cache)
        self.assertIn(4, cache)
        self.assertIn(5, cache)

        self.assertNotIn(6, cache)
        self.assertNotIn(7, cache)
        self.assertNotIn(8, cache)

    def test_lfu_eviction(self):
        self.cache[6, True] = 7

        self.cache[1]
        self.cache[2]
        self.cache[1]
        self.cache[3]
        self.cache[4]
        self.cache[4]

        self.cache[7, True] = 8
        
        self.assertNotIn(5, self.cache)

    def test_lfu_frequency_jumps(self):
        self.cache[6, True] = 7

        self.cache[1]
        self.cache[1]
        self.cache[1]
        self.cache[2]
        self.cache[2]
        self.cache[3]

        self.cache[7, True] = 8
        self.assertNotIn(4, self.cache)

    def test_lfu_callback(self):

        f = Mock() # Mock Callback Function
    
        callback_cache = VolatileLFUCache(capacity=1, callback=f)
        
        callback_cache[1, True] = 2
        callback_cache[2, True] = 3

        f.assert_called_with(1, 2)

    def test_change_item_value(self):
        self.cache = VolatileLFUCache(capacity=6, callback=None)
        keys = [1, 2, 3, 4, 5, 6]
        vals = [2, 3, 4, 5, 6, 7]

        for key, value in zip(keys, vals):
            self.cache[key, True] = value

        self.cache[1, True] = 3
        self.cache[2, True] = 4
        self.cache[3, True] = 5
        self.cache[4, True] = 6
        self.cache[5, True] = 7
        self.cache[6, True] = 8

        self.assertEqual(self.cache[1], 3)
        self.assertEqual(self.cache[2], 4)
        self.assertEqual(self.cache[3], 5)
        self.assertEqual(self.cache[4], 6)
        self.assertEqual(self.cache[5], 7)
        self.assertEqual(self.cache[6], 8)

    def test_delitem(self):
        self.cache[10, False] = 11
        self.cache[11, False] = 12

        self.assertNotIn(1, self.cache)

        del self.cache[2]
        del self.cache[10]

        self.cache[12, False] = 13
        self.cache[13, False] = 14
        self.cache[14, False] = 15
        
        
        self.assertNotIn(3, self.cache)
        self.assertIn(4, self.cache)
        self.assertIn(5, self.cache)
        self.assertIn(11, self.cache)
        self.assertIn(12, self.cache)
        self.assertIn(13, self.cache)
        self.assertIn(14, self.cache)