# pylint: skip-file

import unittest
from unittest.mock import Mock

from src.randcache import VolatileRandomCache


class TestVolatileRandomCache(unittest.TestCase):

    def setUp(self):
        self.cache = VolatileRandomCache(capacity=6, callback=None)

        self.cache[1, True] = 2
        self.cache[2, True] = 3
        self.cache[3, True] = 4
        self.cache[4, True] = 5
        self.cache[5, True] = 6

    def test_cache_length(self):
        self.assertEqual(5, len(self.cache))

        self.cache[1]
        self.cache[2]
        self.cache[3, True] = 5
        self.cache[3, True] = 6
        self.assertEqual(5, len(self.cache))

        del self.cache[1]
        self.assertEqual(4, len(self.cache))

        self.cache.popitem()
        self.assertEqual(3, len(self.cache))

    def test_random_eviction(self):
        self.cache[6, True] = 7
        self.cache[7, True] = 8
        self.cache[8, True] = 9

        self.assertEqual(len(self.cache), 6)

    def test_eviction_no_candidate_items(self):
        cache = VolatileRandomCache(capacity=5)

        cache[1, False] = 2
        cache[2, False] = 3
        cache[3, False] = 4
        cache[4, False] = 5
        cache[5, False] = 6
        cache[6, False] = 7

        self.assertIn(1, cache)
        self.assertIn(2, cache)
        self.assertIn(3, cache)
        self.assertIn(4, cache)
        self.assertIn(5, cache)

        self.assertNotIn(6, self.cache)

    def test_callback(self):
        f = Mock()

        callback_cache = VolatileRandomCache(capacity=4, callback=f)
        
        callback_cache[6, True] = 7
        callback_cache[7, True] = 8
        callback_cache[8, True] = 9
        callback_cache[9, True] = 10
        callback_cache[10, True] = 11

        f.assert_called()

    def test_change_item_value(self):
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

    def test_expiry_with_persistent_keys(self):
        cache = VolatileRandomCache(capacity=4)

        cache[1, False] = 2
        cache[2, True] = 3
        cache[3, False] = 4
        cache[4, False] = 5
        cache[5, True] = 6
        cache[6, True] = 7
        cache[7, True] = 8

        self.assertIn(1, cache)
        self.assertIn(3, cache)
        
        self.assertNotIn(2, cache)
        
