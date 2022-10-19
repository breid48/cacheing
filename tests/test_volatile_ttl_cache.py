from src.randcache import VolatileTTLCache

import asyncio
from unittest import IsolatedAsyncioTestCase


class TestVolatileTTLCache(IsolatedAsyncioTestCase):

    def setUp(self):
        self.cache = VolatileTTLCache(capacity=6, ttl=2)

    async def test_expire_single_key(self):
            
        self.cache.set(1, 2, True)
        self.assertEqual(self.cache.get(1), 2)
        
        await asyncio.sleep(2) # Some task

        self.assertEqual(self.cache.get(1), None)

    async def test_expire_multiple_keys(self):

        self.cache.set(1, 2, True)
        self.cache.set(2, 3, True)
        self.cache.set(3, 4, True)
        self.cache.set(4, 5, True)

        await asyncio.sleep(2) # Some task

        self.cache.set(5, 6, True)

        self.assertEqual(self.cache.get(5), 6)
        self.assertEqual(self.cache.get(1), None)
        self.assertEqual(self.cache.get(2), None)
        self.assertEqual(self.cache.get(3), None)
        self.assertEqual(self.cache.get(4), None)
    
    async def test_persistent_key_non_expiry(self):
            
        self.cache.set(1, 2, False)
        self.cache.set(2, 3, False)
        
        self.assertEqual(self.cache.get(1), 2)
        self.assertEqual(self.cache.get(2), 3)
        
        await asyncio.sleep(2) # Some task

        self.assertEqual(self.cache.get(1), 2)
        self.assertEqual(self.cache.get(2), 3)
    
    async def test_mixed_key_expiry(self):

        self.cache.set(1, 2, False)
        self.cache.set(2, 3, True)
        self.cache.set(3, 4, True)
        self.cache.set(4, 5, False)
        self.cache.set(5, 6, True)

        self.assertEqual(self.cache.get(1), 2)
        self.assertEqual(self.cache.get(2), 3)
        self.assertEqual(self.cache.get(3), 4)
        self.assertEqual(self.cache.get(4), 5)
        self.assertEqual(self.cache.get(5), 6)

        await asyncio.sleep(2) # Some task

        self.assertEqual(self.cache[1], 2)
        self.assertEqual(self.cache.get(2), None)
        self.assertEqual(self.cache.get(3), None)
        self.assertEqual(self.cache[4], 5)
        self.assertEqual(self.cache.get(5), None)
    
    async def test_expire_head(self):
        self.cache.set(1, 2, True)
        
        await asyncio.sleep(2) # Some task

        self.assertEqual(self.cache.get(1), None)
    
    async def test_expire_persistent_head(self):
        self.cache.set(1, 2, False)
        
        await asyncio.sleep(2) # Some task

        self.assertEqual(self.cache.get(1), 2)

    def test_capacity_expiry(self):
        """Ensure Cache evictions occur using an LRU policy when over capacity"""
        self.cache.set(1, 2, True)
        self.cache.set(2, 3, True)
        self.cache.set(3, 4, True)
        self.cache.set(4, 5, True)
        self.cache.set(5, 6, True)
        self.cache.set(6, 7, True)

        self.cache.set(7, 8, True)
        self.cache[2]
        self.cache.set(8, 9, True)

        self.assertNotIn(1, self.cache)
        self.assertNotIn(3, self.cache)        

        self.assertIn(2, self.cache)
        self.assertIn(4, self.cache)
        self.assertIn(5, self.cache)
        self.assertIn(6, self.cache)
        self.assertIn(7, self.cache)

    def test_capacity_expiry_with_persistent_keys(self):
        """Test LRU Evictions with peristent keys"""
        self.cache.set(1, 2, False)
        self.cache.set(2, 3, False)
        self.cache.set(3, 4, True)
        self.cache.set(4, 5, False)
        self.cache.set(5, 6, True)
        self.cache.set(6, 7, True)

        self.cache.set(7, 8, True)
        self.cache[5]
        self.cache.set(8, 9, True)

        self.assertNotIn(3, self.cache)
        self.assertNotIn(6, self.cache)        

        self.assertIn(1, self.cache)
        self.assertIn(2, self.cache)
        self.assertIn(4, self.cache)
        self.assertIn(5, self.cache)
        self.assertIn(7, self.cache)
        self.assertIn(8, self.cache)
