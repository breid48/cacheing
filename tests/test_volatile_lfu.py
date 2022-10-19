# pylint: skip-file

import unittest
from unittest.mock import Mock

from src.randcache import VolatileLFUCache


class TestVolatileLFUCache(unittest.TestCase):

    def setUp(self):
        self.cache = VolatileLFUCache(capacity=6, callback=None)

        self.cache.set(1, 2, True)
        self.cache.set(2, 3, True)
        self.cache.set(3, 4, True)
        self.cache.set(4, 5, True)
        self.cache.set(5, 6, True)

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

        cache.set(1, 2, True)
        cache.set(2, 3, False) # Persist
        cache.set(3, 4, True)
        cache.set(4, 5, True)
        cache.set(5, 6, True)

        cache[1]
        key, value = cache.popitem()
        self.assertEqual(key, 3)

        cache[4]
        cache[5]
        k, v = cache.popitem()
        self.assertEqual(k, 1)

    def test_lfu_set_item_lfu_update(self):
        self.cache.set(6, 7, True)
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

        cache.set(1, 2, False)
        cache.set(2, 3, False)
        cache.set(3, 4, False)
        cache.set(4, 5, False)
        cache.set(5, 6, False)

        cache.set(6, 7, False)
        cache.set(7, 8, False)
        cache.set(8, 9, False)

        self.assertIn(1, cache)
        self.assertIn(2, cache)
        self.assertIn(3, cache)
        self.assertIn(4, cache)
        self.assertIn(5, cache)

        self.assertNotIn(6, cache)
        self.assertNotIn(7, cache)
        self.assertNotIn(8, cache)

    def test_lfu_eviction(self):
        self.cache.set(6, 7, True)

        self.cache[1]
        self.cache[2]
        self.cache[1]
        self.cache[3]
        self.cache[4]
        self.cache[4]

        self.cache.set(7, 8, True)
        
        self.assertNotIn(5, self.cache)

    def test_lfu_frequency_jumps(self):
        self.cache.set(6, 7, True)

        self.cache[1]
        self.cache[1]
        self.cache[1]
        self.cache[2]
        self.cache[2]
        self.cache[3]

        self.cache.set(7, 8, True)
        self.assertNotIn(4, self.cache)

    def test_lfu_callback(self):

        f = Mock() # Mock Callback Function
    
        callback_cache = VolatileLFUCache(capacity=1, callback=f)
        
        callback_cache.set(1, 2, True)
        callback_cache.set(2, 3, True)

        f.assert_called_with(1, 2)

    def test_change_item_value(self):
        self.cache = VolatileLFUCache(capacity=6, callback=None)
        keys = [1, 2, 3, 4, 5, 6]
        vals = [2, 3, 4, 5, 6, 7]

        for key, value in zip(keys, vals):
            self.cache.set(key, value, True)

        self.cache.set(1, 3, True)
        self.cache.set(2, 4, True)
        self.cache.set(3, 5, True)
        self.cache.set(4, 6, True)
        self.cache.set(5, 7, True)
        self.cache.set(6, 8, True)

        self.assertIn(1, self.cache)
        self.assertIn(2, self.cache)
        self.assertIn(3, self.cache)
        self.assertIn(4, self.cache)
        self.assertIn(5, self.cache)
        self.assertIn(6, self.cache)