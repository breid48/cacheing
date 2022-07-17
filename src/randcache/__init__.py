"""
Cacheing library providing various cacheing API's. Inspired
by `cachetools` and Redis, this library supports Redis eviction 
policies that are not available in the `cachetools` python 
standard library. 

Additionally, per-item TTL's are supported by default, as opposed
to the global TTL's offered by `cachetools` TTLCache.

Copyright 2022, Blake Reid.
Licensed under MIT.

"""
import random

from collections import abc, OrderedDict, Counter
from collections.abc import KeysView, ItemsView, ValuesView
from datetime import datetime
from typing import List

from src.randcache.list import (
    _Link, 
    _LinkedList
    )


__all__ = (
    "RCache",
    "LRUCache",
    "VolatileLRUCache",
    "LFUCache",
    "VolatileLFUCache",
    "RandomCache",
    "VolatileRandomCache",
    "TTLCache",
    "VolatileTTLCache",
    "BoundedCache",
)


class RCache(abc.MutableMapping):
    """Cache base-class.

    Evicts the oldest item from the cache
    when the cache reaches maximum capacity.

    Attributes:
        capacity (int): Maximum capacity of the cache.
        callback (callable, optional): Callable defining
        behaviour when an item is evicted from the cache.
        Defaults to None.
  
    """
    __singleton = object()

    def __init__(self, capacity, callback=None):
        """Initializes RCache.

        """        
        self.__cache = {}

        self.__size = 0
        self.__capacity = capacity
        self._callback = callback

    def __setitem__(self, _key, _value):
        while self.__size >= self.__capacity:
            self._evict()

        self.__cache[_key] = _value
        self.__size += 1

    def __getitem__(self, _key):
        return self.__cache[_key]

    def get(self, _key, _default=None):
        try:
            return self[_key]
        except KeyError:
            return _default

    def __delitem__(self, _key):
        del self.__cache[_key]
        self.__size -= 1

    def pop(self, _key, default=__singleton):
        try:
            _value = self.__cache[_key]
        except KeyError:
            if default is self.__singleton:
                raise
            return default
        else:
            del self.__cache[_key]
            self.__size -= 1
            return _value

    def popitem(self):
        """Pop the most recent item from the cache.

        """
        try:
            itm = self.__cache.popitem()
        except KeyError:
            raise KeyError("cache is empty") from None
        else:
            self.__size -= 1
            return itm

    def _evict(self):
        """Evicts an item from the cache determined
        by the relevant algorithm.

        Raises:
            KeyError: Cache is empty.
        """
        try:
            key = next(iter(self))
        except StopIteration:
            raise KeyError("cache is empty") from None

        value = self[key]
        del self.__cache[key]
        self.__size -= 1

        if self._callback:
            self._callback(key, value)

        return key, value

    def __contains__(self, _key):
        return _key in self.__cache

    def __iter__(self):
        return iter(self.__cache)

    def __len__(self):
        return len(self.__cache)

    def __repr__(self):
        return str(self.__cache)

    def keys(self):
        return KeysView(self.__cache)

    def values(self):
        return ValuesView(self.__cache)

    def items(self):
        return ItemsView(self.__cache)

    def update(self, _object: abc.Iterable):
        return self.__cache.update(_object)

    def set_default(self, _key, _value):
        return self.__cache.setdefault(_key, _value)

    def clear(self):
        return self.__cache.clear()

    def get_size(self):
        return self.__size


class LRUCache(RCache):
    """Least Recently Used Cache.

    Attributes:
        capacity (int): Maximum capacity of the cache.
        callback (callable, optional): Callable defining
        behaviour when an item is evicted from the cache.
        Defaults to None.
    
    """
    def __init__(self, capacity, callback=None):
        RCache.__init__(self, capacity, callback)
        self.__lru = OrderedDict()

    def __getitem__(self, _key):
        """Retrieves item and updates it's recency.

        If the item exists, retrieve it from the cache
        and move it to the back of the OrderedDict.

        Args:
            _key (hashable): Hashable Key.
        """
        try:
            _value = RCache.__getitem__(self, _key)
        except KeyError:
            raise KeyError from None
        else:
            self.__lru.move_to_end(_key, last=False)
            return _value

    def __setitem__(self, _key, _value):
        """Add item to the cache and update it's LRU ordering.
        
        If the item exists in the cache, update it's LRU ordering.
        If the item does not exist in the cache, add the item and
        then update it's LRU ordering.

        """
        if not RCache.get(self, _key):
            RCache.__setitem__(self, _key, _value)
            self.__lru[_key] = _value
        
        # Update LRU Ordering 
        self.__lru.move_to_end(_key, last=False)

    def popitem(self):
        """Force eviction of least-recently used item.
        
        """
        try:
            _key, _value = self.__lru.popitem()
        except KeyError:
            raise KeyError("cannot pop from empty cache")
        else:
            RCache.pop(self, _key)
            return (_key, _value)
            
    def _evict(self):
        """Evict the least-recently used item.
        
        Evicts the least-recently used item from
        the cache and updates the LRU ordering.
        If a callback function is specified, the callback
        function is invoked.

        """
        try:
            _key, _value = self.__lru.popitem()
        except KeyError:
            raise KeyError("cannot evict from empty cache")
        else:
            RCache.pop(self, _key)

            if self._callback:
                self._callback(_key, _value)


class VolatileLRUCache(RCache):
    """Volatile Least-Recently Used Cache.

    Evicts key with `expire` field set to true using
    a least-recently used eviction policy.
    
    """
    pass


class LFUCache(RCache):
    pass


class VolatileLFUCache(RCache):
    """Volatile Least-Frequently Used Cache.

    Evicts key with `expire` field set to true using
    a least-frequently used eviction policy.
    
    """
    pass


class RandomCache(RCache):
    pass


class VolatileRandomCache(RCache):
    pass


class TTLCache(LRUCache):
    """
    TTL cache base-class with object-wide fixed
    expiry times.
    
    """
    def __init__(self, ttl):
        self.__cache = {}

        self._linked_list = _LinkedList()

        self._ttl = ttl
        self.__size = 0

    def _expire(func):
        """
        Function decorator. Iterates over the linked list
        and removes expired keys from the cache whenever
        the cache is accessed.

        """
        def expire(self, *args):
            curr = self._linked_list.get_head()

            while curr:
                if curr.expiry <= datetime.now().timestamp():
                    self.__cache.pop(curr.key)
                    self._linked_list.remove_link(curr)
                    curr = curr.next
                else:
                    return func(self, *args)

            return func(self, *args)

        return expire

    @_expire
    def __setitem__(self, _key, _value):
        expiry = datetime.now().timestamp() + self._ttl
        link = _Link(_key, expiry, None)
        self._linked_list.insert_link(link)
        self.__cache[_key] = _value

    @_expire
    def __getitem__(self, _key):
        return self.__cache[_key]

    @_expire
    def __delitem__(self, _key):
        del self.__cache[_key]

    @_expire
    def __contains__(self, _object: object):
        return _object in self.__cache

    @_expire
    def __iter__(self):
        return iter(self.__cache)

    @_expire
    def __len__(self):
        return len(self.__cache)

    @_expire
    def __repr__(self):
        return str(self.__cache)

    @_expire
    def get(self, _key: object, _default=None):
        return self.__cache.get(_key, _default)

    @_expire
    def keys(self):
        return self.__cache.keys()

    @_expire
    def values(self):
        return self.__cache.values()

    @_expire
    def items(self):
        return self.__cache.items()

    @_expire
    def pop(self, _object: object):
        return self.__cache.pop(_object)

    @_expire
    def popitem(self, _object: object):
        return self.__cache.popitem(_object)

    @_expire
    def update(self, _object: abc.Iterable):
        return self.__cache.update(_object)

    @_expire
    def set_default(self, _key, _value):
        return self.__cache.setdefault(_key, _value)

    def clear(self):
        return self.__cache.clear()

    @_expire
    def _get_expiry(self, key):
        head = self._linked_list.get_head()
        while head:
            if head.key == key:
                return head.expiry
            head = head.next

        raise KeyError("key is not in cache")


class VolatileTTLCache(LRUCache):
    pass


class BoundedCache(TTLCache):
    """
    TTL Cache with Randomly Chosen Bounded Expiry Times.

    # TO DO:
        *
        * public access methods?
    """
    def __init__(self, ttl_bound: List[int] = [60, 120]):
        pass

