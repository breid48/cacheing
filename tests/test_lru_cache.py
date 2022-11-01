# pylint: skip-file

import unittest
from unittest.mock import Mock
from collections import OrderedDict

from src.rcache import LRUCache


class TestLRUCache(unittest.TestCase):

    def setUp(self):
        self.cache = LRUCache(capacity=6, callback=None)

        keys = [1, 2, 3, 4, 5]
        vals = [2, 3, 4, 5, 6]

        for key, value in zip(keys, vals):
            self.cache[key] = value

    def test_lru_get_item_lru_update(self):
        self.cache[1]
        k, v = self.cache.popitem()
        self.assertEqual(k, 2)

        self.cache[3]
        self.cache[4]
        self.cache[5]
        k, v = self.cache.popitem()
        self.assertEqual(k, 1)

    def test_lru_set_item_lru_update(self):
        self.cache[6] = 7
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

    def test_lru_evicion(self):
        self.cache[6] = 7
        self.cache[7] = 8
        self.cache[8] = 9
        
        self.assertNotIn(1, self.cache)
        self.assertNotIn(2, self.cache)

    def test_lru_callback(self):

        f = Mock() # Mock Callback Function
    
        callback_cache = LRUCache(capacity=1, callback=f)
        callback_cache[1] = 2
        callback_cache[2] = 3

        f.assert_called_with(1, 2)

    def test_lru_change_item_value(self):
        self.cache = LRUCache(capacity=6, callback=None)
        keys = [1, 2, 3, 4, 5, 6]
        vals = [2, 3, 4, 5, 6, 7]

        for key, value in zip(keys, vals):
            self.cache[key] = value

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

    def test_lru_cache_size(self):
        cache = LRUCache(capacity=51)
        
        for i in range(100):
            cache[i] = i+1
        
        self.assertEqual(51, len(cache))

        cache.popitem()
        cache.popitem()

        self.assertEqual(49, len(cache))
    
    def test_object_equivalence(self):
        cache = LRUCache(capacity=10)
        eqcache = LRUCache(capacity=10)

        cache[1] = 2
        cache[2] = 3
        cache[3] = 4

        eqcache[1] = 2
        eqcache[2] = 3
        eqcache[3] = 4

        self.assertEqual(cache, eqcache)

        eqcache[4] = 5

        self.assertNotEqual(cache, eqcache)
