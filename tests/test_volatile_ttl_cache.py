from src.cacheing import VolatileTTLCache

import asyncio
from unittest import IsolatedAsyncioTestCase


class TestVolatileTTLCache(IsolatedAsyncioTestCase):

    def setUp(self):
        self.cache = VolatileTTLCache(capacity=6, ttl=2)

    async def test_expire_single_key(self):
            
        self.cache[1, True] = 2
        self.assertEqual(self.cache.get(1), 2)
        
        await asyncio.sleep(2) # Some task

        self.assertEqual(self.cache.get(1), None)

    async def test_expire_multiple_keys(self):

        self.cache[1, True] = 2
        self.cache[2, True] = 3
        self.cache[3, True] = 4
        self.cache[4, True] = 5

        await asyncio.sleep(2) # Some task

        self.cache[5, True] = 6

        self.assertEqual(self.cache.get(5), 6)
        self.assertEqual(self.cache.get(1), None)
        self.assertEqual(self.cache.get(2), None)
        self.assertEqual(self.cache.get(3), None)
        self.assertEqual(self.cache.get(4), None)
    
    async def test_persistent_key_non_expiry(self):
            
        self.cache[1, False] = 2
        self.cache[2, False] = 3
        
        self.assertEqual(self.cache.get(1), 2)
        self.assertEqual(self.cache.get(2), 3)
        
        await asyncio.sleep(2) # Some task

        self.assertEqual(self.cache.get(1), 2)
        self.assertEqual(self.cache.get(2), 3)
    
    async def test_mixed_key_expiry(self):

        self.cache[1, False] = 2
        self.cache[2, True] = 3
        self.cache[3, True] = 4
        self.cache[4, False] = 5
        self.cache[5, True] = 6

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
        self.cache[1, True] = 2
        
        await asyncio.sleep(2) # Some task

        self.assertEqual(self.cache.get(1), None)
    
    async def test_expire_persistent_head(self):
        self.cache[1, False] = 2
        
        await asyncio.sleep(2) # Some task

        self.assertEqual(self.cache.get(1), 2)

    def test_capacity_expiry(self):
        """Ensure Cache evictions occur using an LRU policy when over capacity"""
        self.cache[1, True] = 2
        self.cache[2, True] = 3
        self.cache[3, True] = 4
        self.cache[4, True] = 5
        self.cache[5, True] = 6
        self.cache[6, True] = 7

        self.cache[7, True] = 8
        self.cache[2]
        self.cache[8, True] = 9

        self.assertNotIn(1, self.cache)
        self.assertNotIn(3, self.cache)        

        self.assertIn(2, self.cache)
        self.assertIn(4, self.cache)
        self.assertIn(5, self.cache)
        self.assertIn(6, self.cache)
        self.assertIn(7, self.cache)

    def test_capacity_expiry_with_persistent_keys(self):
        """Test LRU Evictions with peristent keys"""
        self.cache[1, False] = 2
        self.cache[2, False] = 3
        self.cache[3, True] = 4
        self.cache[4, False] = 5
        self.cache[5, True] = 6
        self.cache[6, True] = 7

        self.cache[7, True] = 8
        self.cache[5]
        self.cache[8, True] = 9

        self.assertNotIn(3, self.cache)
        self.assertNotIn(6, self.cache)        

        self.assertIn(1, self.cache)
        self.assertIn(2, self.cache)
        self.assertIn(4, self.cache)
        self.assertIn(5, self.cache)
        self.assertIn(7, self.cache)
        self.assertIn(8, self.cache)
