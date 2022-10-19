# pylint: skip-file

import unittest
from unittest.mock import Mock

from src.randcache import VolatileRandomCache


class TestVolatileRandomCache(unittest.TestCase):

    def setUp(self):
        self.cache = VolatileRandomCache(capacity=6, callback=None)

        keys = [1, 2, 3, 4, 5]
        vals = [2, 3, 4, 5, 6]

        self.cache.set(1, 2, True)
        self.cache.set(2, 3, True)
        self.cache.set(3, 4, True)
        self.cache.set(4, 5, True)
        self.cache.set(5, 6, True)


    def test_cache_length(self):
        self.assertEqual(5, len(self.cache))

        self.cache[1]
        self.cache[2]
        self.cache.set(3, 5, True)
        self.cache.set(3, 6, True)
        self.assertEqual(5, len(self.cache))

        del self.cache[1]
        self.assertEqual(4, len(self.cache))

        self.cache.popitem()
        self.assertEqual(3, len(self.cache))

    def test_random_eviction(self):
        self.cache.set(6, 7, True)
        self.cache.set(7, 8, True)
        self.cache.set(8, 9, True)

        self.assertEqual(len(self.cache), 6)

    def test_eviction_no_candidate_items(self):
        cache = VolatileRandomCache(capacity=5)

        cache.set(1, 2, False)
        cache.set(2, 3, False)
        cache.set(3, 4, False)
        cache.set(4, 5, False)
        cache.set(5, 6, False)
        cache.set(6, 7, False)

        self.assertIn(1, cache)
        self.assertIn(2, cache)
        self.assertIn(3, cache)
        self.assertIn(4, cache)
        self.assertIn(5, cache)

        self.assertNotIn(6, self.cache)

    def test_callback(self):
        f = Mock()

        callback_cache = VolatileRandomCache(capacity=4, callback=f)
        
        callback_cache.set(6, 7, True)
        callback_cache.set(7, 8, True)
        callback_cache.set(8, 9, True)
        callback_cache.set(9, 10, True)
        callback_cache.set(10, 11, True)

        f.assert_called()

    def test_change_item_value(self):
        self.cache.set(1, 3, True)
        self.cache.set(2, 4, True)
        self.cache.set(3, 5, True)
        self.cache.set(4, 6, True)
        self.cache.set(5, 7, True)
        self.cache.set(6, 8, True)

        self.assertEqual(self.cache[1], 3)
        self.assertEqual(self.cache[2], 4)
        self.assertEqual(self.cache[3], 5)
        self.assertEqual(self.cache[4], 6)
        self.assertEqual(self.cache[5], 7)
        self.assertEqual(self.cache[6], 8)

    def test_expiry_with_persistent_keys(self):
        cache = VolatileRandomCache(capacity=4)

        cache.set(1, 2, False)
        cache.set(2, 3, True)
        cache.set(3, 4, False)
        cache.set(4, 5, False)
        cache.set(5, 6, True)
        cache.set(6, 7, True)
        cache.set(7, 8, True)

        self.assertIn(1, cache)
        self.assertIn(3, cache)
        
        self.assertNotIn(2, cache)
        
