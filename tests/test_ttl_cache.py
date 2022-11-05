from src.rcache import TTLCache

import asyncio
from unittest import IsolatedAsyncioTestCase



class TestTTLCache(IsolatedAsyncioTestCase):

    def setUp(self):
        self.cache = TTLCache(capacity=6, ttl=2)

    async def test_expire_single_key(self):
            
        self.cache[1] = 2
        self.assertEqual(self.cache.get(1), 2)
        
        await asyncio.sleep(2) # Some task

        self.assertEqual(self.cache.get(1), None)

    async def test_expire_multiple_keys(self):

        self.cache[1] = 2
        self.cache[2] = 3
        self.cache[3] = 4
        self.cache[4] = 5
        
        await asyncio.sleep(2) # Some task

        self.cache[5] = 6

        self.assertEqual(self.cache.get(1), None)
        self.assertEqual(self.cache.get(2), None)
        self.assertEqual(self.cache.get(3), None)
        self.assertEqual(self.cache.get(4), None)
        self.assertEqual(self.cache.get(5), 6)

    async def test_expire_head(self):
        self.cache[1] = 2
        
        await asyncio.sleep(2) # Some task

        self.assertEqual(self.cache.get(1), None)
    
    def test_capacity_eviction(self):
        """Ensure Cache evictions occur using an LRU policy when over capacity"""
        self.cache[1] = 2
        self.cache[2] = 3
        self.cache[3] = 4
        self.cache[4] = 5
        self.cache[5] = 6
        self.cache[6] = 7

        self.cache[7] = 8
        self.cache[2]
        self.cache[8] = 9

        self.assertNotIn(1, self.cache)
        self.assertNotIn(3, self.cache)        

        self.assertIn(2, self.cache)
        self.assertIn(4, self.cache)
        self.assertIn(5, self.cache)
        self.assertIn(6, self.cache)
        self.assertIn(7, self.cache)
    
    async def test_lru_and_time_eviction(self):
        self.cache[1] = 2
        self.cache[2] = 3
        self.cache[3] = 4
        self.cache[4] = 5
        self.cache[5] = 6
        self.cache[6] = 7

        self.cache[7] = 8
        self.cache[2]
        self.cache[3]
        self.cache[8] = 9

        self.assertNotIn(1, self.cache)
        self.assertNotIn(4, self.cache)

        await asyncio.sleep(2) # Some Task

        self.assertEqual(0, len(self.cache))

        self.assertNotIn(2, self.cache)
        self.assertNotIn(3, self.cache)
        self.assertNotIn(5, self.cache)
        self.assertNotIn(6, self.cache)
        self.assertNotIn(7, self.cache)
        self.assertNotIn(8, self.cache)

    async def test_inserting_duplicate_key(self):
        self.cache[1] = 2
        self.cache[2] = 3
        self.cache[3] = 4
        self.cache[4] = 5
        self.cache[5] = 6
        self.cache[6] = 7

        await asyncio.sleep(1) # Some Task
        
        self.cache[1] = 3
        self.cache[2] = 4
        
        self.assertEqual(3, self.cache._list.head.key)

        await asyncio.sleep(1) # Some Task

        self.assertNotIn(3, self.cache)
        self.assertNotIn(4, self.cache)
        self.assertNotIn(5, self.cache)
        self.assertNotIn(6, self.cache)

        self.assertIn(1, self.cache)
        self.assertIn(2, self.cache)

    def test_delitem(self):
        self.cache[1] = 2
        self.cache[2] = 3
        self.cache[3] = 4
        self.cache[4] = 5
        self.cache[5] = 6
        self.cache[6] = 7

        self.assertEqual(1, self.cache._list.head.key)

        del self.cache[1]
        del self.cache[2]

        self.assertNotIn(1, self.cache)
        self.assertNotIn(2, self.cache)
        self.assertEqual(3, self.cache._list.head.key)