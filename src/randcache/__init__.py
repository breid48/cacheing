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
import time
import inspect

from collections import abc, OrderedDict, Counter
from collections.abc import KeysView, ItemsView, ValuesView
from datetime import datetime
from typing import List

from src.randcache.utils import (
    _TTLLink, 
    _TTLLinkedList,
    _LFUNode,
    _LFUFreqNode,
    _LFUList
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
    "FIFOCache",
    "LIFOCache"
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
        if _key not in self.__cache:
            while self.__size >= self.__capacity:
                self._evict()
            self.__cache[_key] = _value
            self.__size += 1
        else:
            self.__cache[_key] = _value

    def __getitem__(self, _key):
        try:
            return self.__cache[_key]
        except KeyError:
            raise KeyError(_key)

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
            _value = self[_key]
            del self[_key]
        except KeyError:
            if default is self.__singleton:
                raise
            return default
        else:
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
        return self.__class__.__name__ + str(self.__cache)

    def keys(self):
        return self.__cache.keys()

    def values(self):
        return self.__cache.values()

    def items(self):
        return self.__cache.items()

    # def update(self, _object: abc.Iterable):
    #     return self.__cache.update(_object)

    # def set_default(self, _key, _value):
    #     return self.__cache.setdefault(_key, _value)
    

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
        """Retrieves item and updates it's priority.

        If the item exists, retrieve it from the cache
        and move it to the back of the OrderedDict.

        Args:
            _key (hashable): Key.
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
        RCache.__setitem__(self, _key, _value)
        self.__lru[_key] = _value
        
        # Update LRU Ordering 
        self.__lru.move_to_end(_key, last=False)

    def __delitem__(self, _key):
        RCache.__delitem__(self, _key)
        del self.__lru[_key]

    def popitem(self):
        """Force eviction of least-recently used item.
        
        """
        try:
            _key, _value = self.__lru.popitem()
        except KeyError:
            raise KeyError("cannot pop from empty cache") from None
        else:
            RCache.__delitem__(self, _key)
            return (_key, _value)
            
    def _evict(self):
        """Evict the least-recently used item.
        
        Called when items are implicitly evicted
        from the cache.

        Evicts the least-recently used item from
        the cache and updates the LRU ordering.
        If a callback function is specified, the callback
        function is invoked.

        """
        try:
            _key, _value = self.popitem()
        except StopIteration:
            raise KeyError("cannot evict from empty cache") from None
        else:
            if self._callback:
                self._callback(_key, _value)


class VolatileLRUCache(LRUCache):
    """Volatile Least-Recently Used Cache.

    Evicts key with `expire` field set to true using
    a least-recently used eviction policy.
    
    """
    pass


class LFUCache(RCache):
    """Least-frequently used cache implementation.

    O(1) insertion, lookup, and deletion.

    References:
        Ketan Shah, Anirban Mitra, and Dhruv Matani, An O(1) algorithm for implementing the LFU cache eviction scheme, (August 16, 2010).

    Args:

    """
    def __init__(self, capacity, callback=None):
        RCache.__init__(self, capacity, callback)
        self.__lfu = _LFUList()

    def __setitem__(self, _key, _value):
        RCache.__setitem__(self, _key, _value)

        # If a node with this `key` already exists,
        # update it's value and access frequency.
        if self.__lfu.cache.get(_key):
            node = self.__lfu.cache[_key]
            node.value = _value
            self.__lfu.access_node(node)

        # Otherwise, create the node and insert
        # it into the DLL.
        else:
            self.__lfu.insert(_key, _value)

    def __getitem__(self, _key):
        try:
            _node = self.__lfu.cache[_key]
        except KeyError:
            raise KeyError(f"{_key}") from None

        self.__lfu.access_node(_node)

        return _node.value

    def __delitem__(self, _key):
        RCache.__delitem__(self, _key)
        _node = self.__lfu.cache[_key]
        self.__lfu.delete_node(_node)

    def popitem(self):
        """Forces eviction of LFU item.

        Raises:
            KeyError: Cache is Empty

        Returns:
            tuple: (Key, Value) pair removed.
        """
        #print(self.__dict__)
        try:
            _key, _value = self.__lfu.delete_lfu_item()
        except KeyError:
            raise KeyError("cannot evict from empty cache") from None
        else:
            RCache.__delitem__(self, _key)
            #print(self.__dict__)
            return (_key, _value)

    def _evict(self):
        try:
            _key, _value = self.__lfu.delete_lfu_item()
        except KeyError:
            raise KeyError("cannot evict from empty cache") from None
        else:
            RCache.__delitem__(self, _key)
            if self._callback:
                self._callback(_key, _value)

    def print_cache(self):
        # REMOVE #
        #        #
        #        #
        #        #
        #        #

        self.__lfu.print_list()
        

# class VolatileLFUCache(LFUCache):
#     """Volatile Least-Frequently Used Cache.

#     Evicts key with `expire` field set to true using
#     a least-frequently used eviction policy.
    
#     """
#     pass


class RandomCache(RCache):
    def __init__(self, capacity, callback=None):
        RCache.__init__(self, capacity, callback)
        
        # To maintain constant time across
        # all operations, maintain a dictionary
        # which tracks the index of each key stored
        # in `self.set`.
        self.set = [] 
        self.idx_map = {}  

    def __setitem__(self, _key, _value):
        RCache.__setitem__(self, _key, _value)
        if _key not in self.idx_map:
            self.set.append(_key)
            self.idx_map[_key] = len(self.set) - 1

    def __delitem__(self, _key):
        RCache.__delitem__(self, _key)
        # In order to perform a deletion without having 
        # to decrement each element of `idx_map`, we
        # swap the last element of `set` with the element 
        # to be deleted, and replace its index in `idx_map`.
        last_elem = self.set[-1]
        index = self.idx_map[_key]
        ssize = len(self.set) - 1

        if index < ssize:
            self.set[index] = last_elem
            self.idx_map[last_elem] = index
        
        self.set.pop()
        del self.idx_map[_key]

    def popitem(self):
        """Force Eviction of Random item.
        
        """
        try:
            _key = self.__get_rand_key()
        except:
            raise KeyError("cannot pop from empty cache") from None
        else:
            _val = RCache.__getitem__(self, _key)
            del self[_key]
            return (_key, _val)

    def _evict(self):
        _key, _value = self.popitem()

        if self._callback:
            self._callback(_key, _value)

    def __get_rand_key(self):
        """Generate a random key from the cache.
        
        """
        return random.choice(self.set)


# class VolatileRandomCache(RCache):
#     pass


class TTLCache(LRUCache):
    """
    TTL cache base-class with global object fixed
    expiry times.
    
    By default, monotonic time is used to track
    key expiry times.
    """
    def __init__(self, capacity, ttl, callback=None, time=time.monotonic):
        LRUCache.__init__(self, capacity, callback)

        self.time = time
        self.__ttl = ttl

        # Dict Mapping Keys to `_TTLLinks`
        # this is primarily used for O(1) 
        # lookup and deletions of `_TTLLinks`
        self.__links = {}
        
        # Linked List of '_TTLLinks'
        # The linked list is 'sorted' in time-ascending
        # order. The key with the nearest expiry time is 
        # at the front of the list.
        self.__list = _TTLLinkedList() 
        
    def expire(_time):
        """Removes expired keys from the cache.
        
        Decorator for class methods. Iterates over the linked 
        list and removes expired keys from the cache whenever
        the cache is accessed.

        """
        def wrap(func):
            
            def wrapped_f(self, *args):
                curr = self.__list.head

                while curr:
                    if curr.expiry < _time():
                        LRUCache.__delitem__(self, curr.key)
                        self.__list.remove(curr)
                        del self.__links[curr.key]
                        curr = curr.next
                    else:
                        return func(self, *args)
                
                return func(self, *args)
            return wrapped_f
        return wrap

    @expire(_time=time.monotonic)
    def __setitem__(self, _key, _value):
        LRUCache.__setitem__(self, _key, _value)
        try:
            link = self.__links[_key]
        except:
            expiry = self.time() + self.__ttl
            self.__links[_key] = link = _TTLLink(_key, expiry, None)
        else:
            self.__list.remove(link)
            expiry = self.time() + self.__ttl
            link.expiry = expiry
        
        self.__list.insert(link)
        print("set 1")

    @expire(_time=time.monotonic)
    def __getitem__(self, _key):
        try:
            _value = LRUCache.__getitem__(self, _key)
        except KeyError:
            raise KeyError(f"{_key}") from None
        else:
            return _value

    @expire(_time=time.monotonic)
    def __delitem__(self, _key):
        try:
            LRUCache.__delitem__(self, _key)
        except KeyError:
            raise KeyError(f"{_key}") from None
        else:
            link = self.__links[_key]
            self.__list.remove(link)
            del self.__links[_key]

    @expire(_time=time.monotonic)
    def __contains__(self, _object: object):
        return RCache.__contains__(_object)

    @expire(_time=time.monotonic)
    def __iter__(self):
        return RCache.__iter__(self)
    
    def _evict(self):
        """Handle evictions when Cache exceeds capacity. 
        Not time-related.

        Invokes callback function whenever an item is evicted.
        
        """
        # Fetch and Evict LRU Item from LRUCache
        _key, _value = LRUCache.popitem()
        
        # Remove References to Link
        link = self.__links[_key]
        self.__list.remove(link)
        del self.__links[_key]

        if self._callback:
            self._callback(_key, _value)
    
    @expire(_time=time.monotonic)
    def __str__(self):
        return RCache.__repr__(self)

    def popitem(self):
        """Evict the LRU item.

        """
        # Fetch and Evict LRU Item from LRUCache
        _key, _value = LRUCache.popitem()
        
        # Remove References to Link
        link = self.__links[_key]
        self.__list.remove(link)
        del self.__links[_key]
            
    """

    @expire(_time=time.monotonic())
    def update(self, _object: abc.Iterable):
        return self.__cache.update(_object)

    @expire(_time=time.monotonic())
    def set_default(self, _key, _value):
        return self.__cache.setdefault(_key, _value)

    def clear(self):
        return self.__cache.clear()

    """

# class VolatileTTLCache(LRUCache):
#     pass


# class BoundedCache(TTLCache):
#     """
#     TTL Cache with Randomly Chosen Bounded Expiry Times.

#     # TO DO:
#         *
#         * public access methods?
#     """
#     def __init__(self, ttl_bound: List[int] = [60, 120]):
#         pass

# class FIFOCache:
#     pass

# class LIFOCache:
#     pass

