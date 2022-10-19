# pylint: skip-file

import unittest
from unittest.mock import Mock

from src.randcache import VolatileLRUCache


class TestVolatileLRUCache(unittest.TestCase):

    def setUp(self):
        self.cache = VolatileLRUCache(capacity=6, callback=None)

        self.cache.set(1, 2, True)
        self.cache.set(2, 3, True)
        self.cache.set(3, 4, True)
        self.cache.set(4, 5, True)
        self.cache.set(5, 6, True)

    def test_get_item_lru_update(self):

        self.cache[1]
        key, value = self.cache.popitem()
        self.assertEqual(key, 2)

        self.cache[3]
        self.cache[4]
        self.cache[5]
        k, v = self.cache.popitem()
        self.assertEqual(k, 1)
    
    def test_get_item_lru_update_with_persistent_keys(self):
        cache = VolatileLRUCache(capacity=6, callback=None)

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

    def test_lru_set_item_lru_update(self):
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

    def test_lru_eviction(self):
        self.cache.set(6, 7, True)
        self.cache.set(7, 8, True)
        self.cache.set(8, 9, True)
        
        self.assertNotIn(1, self.cache)
        self.assertNotIn(2, self.cache)

    def test_lru_callback(self):

        f = Mock() # Mock Callback Function
    
        callback_cache = VolatileLRUCache(capacity=1, callback=f)
        
        callback_cache.set(1, 2, True)
        callback_cache.set(2, 3, True)

        f.assert_called_with(1, 2)

    def test_change_item_value(self):
        self.cache = VolatileLRUCache(capacity=6, callback=None)
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