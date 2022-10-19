from src.randcache import VTTLCache

import asyncio
from unittest import IsolatedAsyncioTestCase


class TestVTTLCache(IsolatedAsyncioTestCase):

    def setUp(self):
        self.cache = VTTLCache(capacity=6)

    async def test_expire_single_key(self):
            
        self.cache.set(1, 2, 2)
        self.assertEqual(self.cache.get(1), 2)
        
        await asyncio.sleep(2) # Some task

        self.assertEqual(self.cache.get(1), None)

    async def test_expire_multiple_keys(self):

        self.cache.set(1, 2, 2)
        self.cache.set(2, 3, 2)
        self.cache.set(3, 4, 2)
        self.cache.set(4, 5, 2)

        await asyncio.sleep(2) # Some task

        self.cache.set(5, 6, 2)

        self.assertEqual(self.cache.get(5), 6)
        self.assertEqual(self.cache.get(1), None)
        self.assertEqual(self.cache.get(2), None)
        self.assertEqual(self.cache.get(3), None)
        self.assertEqual(self.cache.get(4), None)
    
    async def test_expiry_different_ttls(self):  
        self.cache.set(1, 2, 2)
        self.cache.set(2, 3, 5)
        self.cache.set(3, 4, 1)
        self.cache.set(4, 5, 6)
        self.cache.set(5, 6, 3)
        
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
        self.cache.set(1, 2, 40)
        self.cache.set(2, 3, 50)
        self.cache.set(3, 4, 60)
        self.cache.set(4, 5, 30)
        self.cache.set(5, 6, 20)
        self.cache.set(6, 7, 25)

        self.cache.set(7, 8, 35)
        self.cache[2]
        self.cache[4]
        self.cache.set(8, 9, 95)
        self.cache.set(9, 10, 15)

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
        self.cache.set(1, 2, 4)
        self.cache.set(2, 3, 5)
        self.cache.set(3, 4, 6)
        self.cache.set(4, 5, 3)
        self.cache.set(5, 6, 2)
        self.cache.set(6, 7, 1)

        self.cache[1]
        self.cache[2]

        self.cache.set(7, 8, 8)
        self.cache.set(8, 9, 11)
        self.cache.set(9, 11, 13)

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
