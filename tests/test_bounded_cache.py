from src.randcache import BoundedTTLCache

import asyncio
from unittest import IsolatedAsyncioTestCase


class TestBoundedCache(IsolatedAsyncioTestCase):

    def setUp(self):
        self.cache = BoundedTTLCache(capacity=5, ttl_min=1, ttl_max=3)

    async def test_expire_single_key(self):
            
        self.cache[1] = 2
        self.assertEqual(self.cache.get(1), 2)

        await asyncio.sleep(3) # Some task

        self.assertEqual(self.cache.get(1), None)

    async def test_expire_multiple_keys(self):

        self.cache[1] = 2
        self.cache[2] = 3
        self.cache[3] = 4
        self.cache[4] = 5

        self.assertEqual(self.cache.get(1), 2)
        self.assertEqual(self.cache.get(2), 3)
        self.assertEqual(self.cache.get(3), 4)
        
        await asyncio.sleep(3) # Some task

        self.assertEqual(self.cache.get(1), None)
        self.assertEqual(self.cache.get(2), None)
        self.assertEqual(self.cache.get(3), None)

    async def test_expire_head(self):
        self.cache[1] = 2
        
        await asyncio.sleep(3) # Some task

        self.assertEqual(self.cache.get(1), None)
