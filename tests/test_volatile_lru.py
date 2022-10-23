# pylint: skip-file

import unittest
from unittest.mock import Mock

from src.randcache import VolatileLRUCache


class TestVolatileLRUCache(unittest.TestCase):

    def setUp(self):
        self.cache = VolatileLRUCache(capacity=6, callback=None)

        self.cache[1, True] = 2
        self.cache[2, True] = 3
        self.cache[3, True] = 4
        self.cache[4, True] = 5
        self.cache[5, True] = 6

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

    def test_lru_set_item_lru_update(self):
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

    def test_lru_eviction(self):
        self.cache[6, True] = 7
        self.cache[7, True] = 8
        self.cache[8, True] = 9
        
        self.assertNotIn(1, self.cache)
        self.assertNotIn(2, self.cache)

    def test_lru_callback(self):

        f = Mock() # Mock Callback Function
    
        callback_cache = VolatileLRUCache(capacity=1, callback=f)
        
        callback_cache[1, True] = 2
        callback_cache[2, True] = 3

        f.assert_called_with(1, 2)

    def test_change_item_value(self):
        self.cache = VolatileLRUCache(capacity=6, callback=None)
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

        self.assertIn(1, self.cache)
        self.assertIn(2, self.cache)
        self.assertIn(3, self.cache)
        self.assertIn(4, self.cache)
        self.assertIn(5, self.cache)
        self.assertIn(6, self.cache)