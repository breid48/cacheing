# pylint: skip-file

import unittest
from unittest.mock import Mock

from typing import ItemsView, KeysView, ValuesView

from src.randcache import VolatileCache


class TestVolatileCache(unittest.TestCase):

    def setUp(self):
        self.cache = VolatileCache(capacity=6, callback=None)

        self.cache.set(1, 2, False)
        self.cache.set(2, 3, True)
        self.cache.set(3, 4, True)
        self.cache.set(4, 5, True)
        self.cache.set(5, 6, True)

    def test_set(self):
        self.assertIn(1, self.cache)
        self.assertIn(2, self.cache)
        self.assertIn(3, self.cache)
        self.assertIn(4, self.cache)
        self.assertIn(5, self.cache)

    def test_get_item(self):
        self.assertEqual(self.cache[1], 2)
        self.assertEqual(self.cache[2], 3)
        self.assertEqual(self.cache[3], 4)
        self.assertEqual(self.cache[4], 5)
        self.assertEqual(self.cache[5], 6)

    def test_get_item_raises_key_error(self):
        self.assertRaises(KeyError, lambda: self.cache[100])

    def test_delete_item(self):
        self.assertIn(1, self.cache)
        del self.cache[1]
        self.assertNotIn(1, self.cache)

        self.assertIn(2, self.cache)
        del self.cache[2]
        self.assertNotIn(2, self.cache)

        self.assertIn(5, self.cache)
        del self.cache[5]
        self.assertNotIn(5, self.cache)

    def test_delete_item_raises_key_error(self):
        with self.assertRaises(KeyError):
            del self.cache[100]

    def test_contains(self):
        self.assertEqual(1 in self.cache, True)
        self.assertEqual(2 in self.cache, True)
        self.assertEqual(5 in self.cache, True)

    def test_not_contains(self):
        self.assertEqual("bar" in self.cache, False)
        self.assertEqual(11 in self.cache, False)

    def test_len(self):
        cache = VolatileCache(capacity=128)

        for i in range(128):
            cache.set(i, i+1, True)

        self.assertEqual(128, len(cache))

        del cache[1]

        self.assertEqual(127, len(cache))

    def test_repr(self):   
        self.assertEqual(repr(self.cache), 'VolatileCache{1: 2, 2: 3, 3: 4, 4: 5, 5: 6}')

    def test_get(self):
        self.assertEqual(self.cache.get(1, None), 2)
        self.assertEqual(self.cache.get(2, None), 3)
        self.assertEqual(self.cache.get(3), 4)
        self.assertEqual(self.cache.get(5), 6)

    def test_get_default_is_none(self):
        self.assertEqual(self.cache.get(100), None)

    def test_get_default(self):
        self.assertEqual(self.cache.get(100, "default"), "default")

    def test_keys_view(self):
        self.assertIsInstance(self.cache.keys(), KeysView)

    def test_keys_contains(self):
        self.assertIn(1, self.cache.keys())

    def test_values_view(self):
        self.assertIsInstance(self.cache.values(), ValuesView)

    def test_values_expression(self):
        self.assertIn(2, self.cache.values())

    def test_items_view(self):
        self.assertIsInstance(self.cache.items(), ItemsView)

    def test_items_contains(self):
        self.assertIn((2, 3), self.cache.items())

    def test_pop(self):
        self.assertEqual(self.cache.pop(1), 2)

    def test_pop_default(self):
        self.assertEqual(self.cache.pop(200, default="d"), "d")

    def test_pop_false_member(self):
        self.assertRaises(KeyError, lambda: self.cache.pop(100))

    def test_evict(self):
        cache = VolatileCache(capacity=10)
        cache.set(1, 2, True)
        cache.set(2, 3, True)
        cache.set(3, 4, True)

        cache._evict()
        self.assertNotIn(1, cache)
    
    def test_eviction_option(self):
        cache = VolatileCache(capacity=10)
        cache.set(1, 2, False) # Key is set to persist, should not expire
        cache.set(2, 3, True)
        cache.set(3, 4, True)

        cache._evict()
        self.assertNotIn(2, cache)

    def test_memory_overflow(self):
        cache = VolatileCache(capacity=10)

        for i in range(10):
            cache.set(i, i+1, True)

        cache.set(11, 12, True)

        self.assertEqual(len(cache), 10)
        self.assertIn(11, cache)

    def test_object_equivalence(self):
        cache = VolatileCache(capacity=10)
        eqcache = VolatileCache(capacity=10)

        cache.set(1, 2, True)
        cache.set(2, 3, True)
        cache.set(3, 4, True)

        eqcache.set(1, 2, True)
        eqcache.set(2, 3, True)
        eqcache.set(3, 4, True)

        self.assertEqual(cache, eqcache)

        eqcache.set(4, 5, True)

        self.assertNotEqual(cache, eqcache)

    def test_cache_size(self):
        self.assertEqual(len(self.cache), 5)

    def test_cache_size_update(self):
        del self.cache[1]
        self.assertEqual(len(self.cache), 4)
    
    def test_cache_pop_size_update(self):
        self.cache.pop(1)
        self.assertEqual(len(self.cache), 4)

    def test_cache_popitem_size_update(self):
        self.cache.popitem()
        self.assertEqual(len(self.cache), 4)