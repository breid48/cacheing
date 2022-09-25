# pylint: skip-file

import unittest

from typing import ItemsView, KeysView, ValuesView

from src.randcache import RCache


class TestRCache(unittest.TestCase):

    def setUp(self):
        self.cache = RCache(capacity=128)

        keys = [1, 1.01, (1, 0), "foo"]
        vals = [11, 1.01, 10, "bar"]

        for k, v in zip(keys, vals):
            self.cache[k] = v

    def test_set_item(self):
        self.assertIn(1, self.cache)
        self.assertIn(1.01, self.cache)
        self.assertIn((1, 0), self.cache)
        self.assertIn("foo", self.cache)

    def test_get_item(self):
        self.assertEqual(self.cache[1], 11)
        self.assertEqual(self.cache[1.01], 1.01)
        self.assertEqual(self.cache[(1, 0)], 10)
        self.assertEqual(self.cache["foo"], "bar")

    def test_get_item_raises_key_error(self):
        self.assertRaises(KeyError, lambda: self.cache[2])

    def test_delete_item(self):
        self.assertIn(1, self.cache)
        del self.cache[1]
        self.assertNotIn(1, self.cache)

        self.assertIn(1.01, self.cache)
        del self.cache[1.01]
        self.assertNotIn(1.01, self.cache)

    def test_delete_item_raises_key_error(self):
        with self.assertRaises(KeyError):
            del self.cache[2]

    def test_contains(self):
        self.assertEqual(1 in self.cache, True)
        self.assertEqual(1.01 in self.cache, True)
        self.assertEqual("foo" in self.cache, True)

    def test_not_contains(self):
        self.assertEqual("bar" in self.cache, False)
        self.assertEqual(1111 in self.cache, False)

    def test_iter(self):
        for k in iter(self.cache):
            self.assertIn(k, self.cache.keys())

    def test_len(self):
        cache = RCache(capacity=128)

        for i in range(128):
            cache[i] = i

        self.assertEqual(128, len(cache))

        del cache[1]

        self.assertEqual(127, len(cache))

    def test_repr(self):   
        self.assertEqual(repr(self.cache), "RCache{1: 11, 1.01: 1.01, (1, 0): 10, 'foo': 'bar'}")

    def test_get(self):
        self.assertEqual(self.cache.get(1, None), 11)
        self.assertEqual(self.cache.get(1.01, None), 1.01)
        self.assertEqual(self.cache.get("foo"), "bar")
        self.assertEqual(self.cache.get((1, 0)), 10)

    def test_get_default_is_none(self):
        self.assertEqual(self.cache.get(2), None)

    def test_get_default(self):
        self.assertEqual(self.cache.get(2, "default"), "default")

    def test_keys_view(self):
        self.assertIsInstance(self.cache.keys(), KeysView)

    def test_keys_expression(self):
        self.assertIn(1, self.cache.keys())

    def test_values_view(self):
        self.assertIsInstance(self.cache.values(), ValuesView)

    def test_values_expression(self):
        self.assertIn(11, self.cache.values())

    def test_items_view(self):
        self.assertIsInstance(self.cache.items(), ItemsView)

    def test_items_expression(self):
        self.assertIn((1, 11), self.cache.items())

    def test_pop(self):
        self.assertEqual(self.cache.pop(1), 11)

    def test_pop_default(self):
        self.assertEqual(self.cache.pop(200, default="d"), "d")

    def test_pop_false_member(self):
        self.assertRaises(KeyError, lambda: self.cache.pop(2))

    # def test_evict(self):
    #     cache = RCache(capacity=10)
    #     cache[1] = 2
    #     cache[2] = 3
    #     cache[3] = 4

    #     cache._evict()
    #     self.assertNotIn(1, cache)

    def test_cache_size_overflow(self):
        cache = RCache(capacity=10)

        for i in range(10):
            cache[i] = i+1

        cache[11] = 12

        self.assertEqual(len(cache), 10)
        self.assertIn(11, cache)

    def test_object_equivalence(self):
        cache = RCache(capacity=10)
        eqcache = RCache(capacity=10)

        cache[1] = 2
        cache[2] = 3
        cache[3] = 4

        eqcache[1] = 2
        eqcache[2] = 3
        eqcache[3] = 4

        self.assertEqual(cache, eqcache)

        eqcache[4] = 5

        self.assertNotEqual(cache, eqcache)

    def test_cache_size(self):
        self.assertEqual(len(self.cache), 4)

    def test_cache_size_after_deletion(self):
        del self.cache[1]
        self.assertEqual(len(self.cache), 3)
    
    def test_cache_size_after_pop(self):
        self.cache.pop(1)
        self.assertEqual(len(self.cache), 3)

    def test_cache_size_after_popitem(self):
        self.cache.popitem()
        self.assertEqual(len(self.cache), 3)