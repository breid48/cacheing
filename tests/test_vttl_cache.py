from src.randcache import VTTLCache

import asyncio
from unittest import IsolatedAsyncioTestCase


class TestVTTLCache(IsolatedAsyncioTestCase):

    def setUp(self):
        self.cache = VTTLCache(capacity=6)

    async def test_expire_single_key(self):
            
        self.cache[1, 2] = 2
        self.assertEqual(self.cache.get(1), 2)
        
        await asyncio.sleep(2) # Some task

        self.assertEqual(self.cache.get(1), None)

    async def test_expire_multiple_keys(self):

        self.cache[1, 2] = 2
        self.cache[2, 2] = 3
        self.cache[3, 2] = 4
        self.cache[4, 2] = 5

        await asyncio.sleep(2) # Some task

        self.cache[5, 2] = 6

        self.assertEqual(self.cache.get(5), 6)
        self.assertEqual(self.cache.get(1), None)
        self.assertEqual(self.cache.get(2), None)
        self.assertEqual(self.cache.get(3), None)
        self.assertEqual(self.cache.get(4), None)
    
    async def test_expiry_different_ttls(self):  
        self.cache[1, 2] = 2
        self.cache[2, 5] = 3
        self.cache[3, 1] = 4
        self.cache[4, 6] = 5
        self.cache[5, 3] = 6
        
        self.assertEqual(self.cache.get(1), 2)
        self.assertEqual(self.cache.get(2), 3)
        
        await asyncio.sleep(3) # Some task

        self.assertEqual(self.cache.get(1), None)
        self.assertEqual(self.cache.get(2), 3)
        self.assertEqual(self.cache.get(3), None)
        self.assertEqual(self.cache.get(4), 5)
        self.assertEqual(self.cache.get(5), None)

    def test_lru_expiry(self):
        """Ensure Cache evictions occur using an LRU policy when over capacity"""
        self.cache[1, 40] = 2
        self.cache[2, 50] = 3
        self.cache[3, 60] = 4
        self.cache[4, 30] = 5
        self.cache[5, 20] = 6
        self.cache[6, 25] = 7

        self.cache[7, 35] = 8
        self.cache[2]
        self.cache[4]
        self.cache[8, 95] = 9
        self.cache[9, 15] = 10

        self.assertNotIn(1, self.cache)
        self.assertNotIn(3, self.cache)        
        self.assertNotIn(5, self.cache)

        self.assertIn(2, self.cache)
        self.assertIn(4, self.cache)
        self.assertIn(6, self.cache)
        self.assertIn(7, self.cache)
        self.assertIn(8, self.cache)
        self.assertIn(9, self.cache)
    
    async def test_lru_expiry_and_time_expiry(self):
        self.cache[1, 4] = 2
        self.cache[2, 5] = 3
        self.cache[3, 6] = 4
        self.cache[4, 3] = 5
        self.cache[5, 2] = 6
        self.cache[6, 1] = 7

        self.cache[1]
        self.cache[2]

        self.cache[7, 8] = 8
        self.cache[8, 11] = 9
        self.cache[9, 13] = 11

        await asyncio.sleep(1)

        self.assertIn(1, self.cache)
        self.assertIn(2, self.cache)
        self.assertIn(7, self.cache)
        self.assertIn(8, self.cache)
        self.assertIn(9, self.cache)

        self.assertNotIn(3, self.cache)
        self.assertNotIn(4, self.cache)
        self.assertNotIn(5, self.cache)
        self.assertNotIn(6, self.cache)

    def test_float_expiry(self):
        return
