from src.randcache import TTLCache

import asyncio
from unittest import IsolatedAsyncioTestCase



class TestTTLCache(IsolatedAsyncioTestCase):

    def setUp(self):
        self.cache = TTLCache(capacity=6, ttl=3)

    async def test_expire_single_key(self):
            
        self.cache[1] = 2
        
        await asyncio.sleep(3) # Some task

        self.assertEqual(self.cache.get(1), None)

    async def test_expire_multiple_keys(self):

        self.cache[1] = 2
        self.cache[2] = 3
        self.cache[3] = 4
        self.cache[4] = 5
        
        await asyncio.sleep(3) # Some task

        self.cache[5] = 6

        self.assertEqual(self.cache.get(1), None)
        self.assertEqual(self.cache.get(2), None)
        self.assertEqual(self.cache.get(3), None)
        self.assertEqual(self.cache.get(4), None)
        self.assertEqual(self.cache.get(5), 6)

    async def test_expire_head(self):
        self.cache[1] = 2
        
        await asyncio.sleep(3) # Some task

        self.assertEqual(self.cache.get(1), None)
