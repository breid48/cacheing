"""
Cacheing library providing various cacheing API's. Inspired
by `cachetools` and Redis, this library supports Redis-like eviction
policies that are not available in the `cachetools` python
standard library.

Per-item TTL's are supported in the 'VTTLCache', as opposed
to the global TTL's offered by `cachetools` TTLCache.

Copyright 2022, Blake Reid.
Licensed under MIT.

"""
import random
import time

from collections import OrderedDict, Counter
from collections.abc import MutableMapping, Iterable, KeysView, ItemsView, ValuesView
from typing import List

from src.cacheing.utils import (
    _TTLLink,
    _TTLLinkedList,
    LFULinkedList,
    LFUNode
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
    "BoundedTTLCache"
)


class RCache(MutableMapping):
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
        self.__cache = {}

        self.__size = 0 # Number of Items in the Cache
        self.__capacity = capacity
        self._callback = callback

    @property
    def capacity(self):
        return self.__capacity

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
            raise KeyError(_key) from None

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
        """Pop the most recent item from the cache."""
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
        return "{}{}".format(self.__class__.__name__, self.__cache)

    def keys(self):
        return self.__cache.keys()

    def values(self):
        return self.__cache.values()

    def items(self):
        return self.__cache.items()

    def __eq__(self, obj):
        if isinstance(obj, RCache):
            if self.__dict__ == obj.__dict__:
                return True
        return False


class VolatileCache:
    """Base class for volatile-type caches.

    Supports cases of per-item persistance and non-evictions.

    Attributes:
        capacity (int): Maximum capacity of the cache.
        callback (callable, optional): Callable defining
        behaviour when an item is evicted from the cache.
        Defaults to None.
    """
    __singleton = object()

    def __init__(self, capacity, callback=None):
        self.__cache = {}

        self.__size = 0
        self.__capacity = capacity
        self._callback = callback

        # Dict containing items which expire
        self._expires_map = {}

    @property
    def capacity(self):
        return self.__capacity

    def __setitem__(self, _keymeta, _value):
        _key, expires = _keymeta

        if _key not in self.__cache:
            while self.__size >= self.__capacity and self._expires_map:
                self._evict()
            if self.__size < self.__capacity: # Otherwise, new data item is discarded
                self.__cache[_key] = _value
                if expires:
                    self._expires_map[_key] = _value
                self.__size += 1
        else:
            self.__cache[_key] = _value
            if expires:
                self._expires_map[_key] = _value

    def __getitem__(self, _key):
        try:
            return self.__cache[_key]
        except KeyError:
            raise KeyError(_key) from None

    def get(self, _key, _default=None):
        """If key does not exist in the cache, returns default.

        Args:
            _key (hashable): Item key.
            _default (object, optional): Defaults to None.
        """
        try:
            return self[_key]
        except KeyError:
            return _default

    def __delitem__(self, _key):
        del self.__cache[_key]
        self._expires_map.pop(_key, None)
        self.__size -= 1

    def pop(self, _key, default=__singleton):
        """_summary_

        Args:
            _key (_type_): _description_
            default (_type_, optional): _description_. Defaults to __singleton.

        Returns:
            _type_: _description_
        """
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
        """Pop the most recent item from the cache."""
        try:
            key, value = self.__cache.popitem()
            self._expires_map.pop(key, None)
        except KeyError:
            raise KeyError("cache is empty") from None
        else:
            self.__size -= 1
            return (key, value)

    def _evict(self):
        """Evicts an item from the cache determined
        by the relevant algorithm.

        Raises:
            KeyError: Cache is empty.
        """
        try:
            key = next(iter(self._expires_map))
        except StopIteration:
            raise KeyError("no candidate keys available to evict") from None

        value = self[key]
        del self.__cache[key]
        del self._expires_map[key]
        self.__size -= 1

        if self._callback:
            return self._callback(key, value)

        return key, value

    def __contains__(self, _key):
        return _key in self.__cache

    def __iter__(self):
        return iter(self.__cache)

    def __len__(self):
        return len(self.__cache)

    def __repr__(self):
        return "{}{}".format(self.__class__.__name__, self.__cache)

    def keys(self):
        return self.__cache.keys()

    def values(self):
        return self.__cache.values()

    def items(self):
        return self.__cache.items()

    def __eq__(self, obj):
        if isinstance(obj, VolatileCache):
            if self.__dict__ == obj.__dict__:
                return True
        return False


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
        self._lru = OrderedDict()

    def __getitem__(self, _key):
        """Retrieves item from the cache.

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
            self._lru.move_to_end(_key, last=False)
            return _value

    def __setitem__(self, _key, _value):
        """Add item to the cache..

        If the item exists in the cache, update it's LRU ordering.
        If the item does not exist in the cache, add the item and
        then update it's LRU ordering.

        Args:
            _key (hashable): Item Key.
            _value (object): Item Value.
        """
        RCache.__setitem__(self, _key, _value)
        self._lru[_key] = _value

        # Update LRU Ordering
        self._lru.move_to_end(_key, last=False)

    def __delitem__(self, _key):
        RCache.__delitem__(self, _key)
        del self._lru[_key]

    def popitem(self):
        """Force eviction of least-recently used item."""
        try:
            _key, _value = self._lru.popitem()
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
        except KeyError:
            raise KeyError("cannot evict from empty cache") from None
        else:
            if self._callback:
                self._callback(_key, _value)


class VolatileLRUCache(VolatileCache):
    """Volatile Least-Recently Used Cache.

    Evicts key with `expire` field set to True using
    a least-recently used eviction policy.

    Persists keys with the 'expire' field set to False.

    If the cache capacity is reached and there are no
    keys to expire, new data is discarded.

    Attributes:
        capacity (int): Maximum capacity of the cache.
        callback (callable, optional): Callable defining
        behaviour when an item is evicted from the cache.
        Defaults to None.
    """
    def __init__(self, capacity, callback=None):
        VolatileCache.__init__(self, capacity, callback)
        self._lru = OrderedDict()

    def __setitem__(self, _keymeta, _value):
        """Set an item in the cache.

        Args:
            _expire (bool): Defines if this cache item expires.
            _keymeta (tuple): Item Key & Expire Field.
            _value (object): Item Value.

        """
        _key, _expires = _keymeta

        if not isinstance(_expires, bool):
            raise TypeError("{} is not bool".format(_expires))

        VolatileCache.__setitem__(self, _keymeta, _value)

        if _expires:
            self._lru[_key] = _value

            # Update LRU Ordering
            self._lru.move_to_end(_key, last=False)

    def __getitem__(self, _key):
        """Retrieves item and updates it's priority.

        Args:
            _key (object): Key.
        """
        try:
            _value = VolatileCache.__getitem__(self, _key)
        except KeyError:
            raise KeyError from None
        else:
            if self._expires_map.get(_key): # Key Expires
                self._lru.move_to_end(_key, last=False)
            return _value

    def __delitem__(self, _key):
        VolatileCache.__delitem__(self, _key)
        if self._lru[_key]:
            del self._lru[_key]

    def popitem(self):
        """Pop non-persistent LRU item from the cache.

        If no candidate keys are available, raises KeyError.
        """
        try:
            _key, _value = self._lru.popitem()
        except KeyError:
            # Cache is at full-capacity and there are
            # no candidate keys to pop.
            raise KeyError("no candidate keys") from None
        else:
            VolatileCache.__delitem__(self, _key)
            return (_key, _value)

    def _evict(self):
        try:
            _key, _value = self.popitem()
        except KeyError:
            raise KeyError("cannot evict from empty cache") from None
        else:
            if self._callback:
                self._callback(_key, _value)


class LFUCache(RCache):
    """Least-frequently used cache implementation.

    O(1) insertion, lookup, and deletion.

    References:
        Ketan Shah, Anirban Mitra, and Dhruv Matani, An O(1) algorithm for implementing the LFU
        cache eviction scheme, (August 16, 2010).

    Attributes:
        capacity (int): Maximum capacity of the cache.
        callback (callable, optional): Callable defining
        behaviour when an item is evicted from the cache.
        Defaults to None.
    """
    def __init__(self, capacity, callback=None):
        RCache.__init__(self, capacity=capacity, callback=callback)

        self.__lfu = LFULinkedList()
        self.node_cache = self.__lfu.node_cache

    def __setitem__(self, _key, _value):
        RCache.__setitem__(self, _key, _value)

        if _key in self.node_cache:
            self.__lfu.increment(_key)
        else:
            self.__lfu.insert(_key)

    def __getitem__(self, _key):
        _value = RCache.__getitem__(self, _key)
        self.__lfu.increment(_key)

        return _value

    def __delitem__(self, _key):
        RCache.__delitem__(self, _key)
        self.__lfu.delete(_key)

    def popitem(self):
        """Force eviction of LFU item.

        Returns:
            tuple: LFU item key, value pair.
        """
        key = self.__lfu.popleft()
        value = RCache.__getitem__(self, key)
        RCache.__delitem__(self, key)
        return (key, value)

    def _evict(self):
        key, value = self.popitem()
        if self._callback:
            self._callback(key, value)


class VolatileLFUCache(VolatileCache):
    """Volatile Least-Frequently Used Cache.

    Evicts key with `expire` field set to true using
    a least-frequently used eviction policy.

    Attributes:
        capacity (int): Maximum capacity of the cache.
        callback (callable, optional): Callable defining
        behaviour when an item is evicted from the cache.
        Defaults to None.
    """
    def __init__(self, capacity, callback=None):
        VolatileCache.__init__(self, capacity, callback)
        self.__lfu = LFULinkedList()
        self.node_cache = self.__lfu.node_cache

    def __setitem__(self, _keymeta, _value):
        _key, _expires = _keymeta

        if not isinstance(_expires, bool):
            raise TypeError("{} is not bool".format(_expires))

        VolatileCache.__setitem__(self, _keymeta, _value)

        # Check if a node with this key already exists.
        # If a node sharing this key exists in the LFU stream
        # and it's expiry is CHANGED to False, remove
        # it from the LFU stream:
        if _key in self.node_cache and not _expires:
            self.__lfu.delete(_key)

        # Otherwise, increment it's access frequency:
        elif _key in self.node_cache and _expires:
            self.__lfu.increment(_key)

        # If the item does not exist, and it's expiry is
        # set to True - insert it into the linked list:
        elif _key not in self.node_cache and _expires:
            self.__lfu.insert(_key)

    def __getitem__(self, _key):
        _value = VolatileCache.__getitem__(self, _key)

        if _key in self.node_cache:
            self.__lfu.increment(_key)

        return _value

    def __delitem__(self, _key):
        VolatileCache.__delitem__(self, _key)

        if _key in self.node_cache:
            self.__lfu.delete(_key)

    def popitem(self):
        # If there's no items to expire, return None
        if not self._expires_map:
            return (None, None)

        _key = self.__lfu.popleft()
        _value = VolatileCache.__getitem__(self, _key)
        VolatileCache.__delitem__(self, _key)
        return (_key, _value)

    def _evict(self):
        """Evicts non-persistent LFU Item."""
        _key, _value = self.popitem()
        if self._callback:
            self._callback(_key, _value)


class RandomCache(RCache):
    """Cache with Random Eviction Policy.

    Attributes:
        capacity (int): Maximum capacity of the cache.
        callback (callable, optional): Callable defining
        behaviour when an item is evicted from the cache.
        Defaults to None.
    """
    def __init__(self, capacity, callback=None):
        RCache.__init__(self, capacity, callback)

        self.set = []
        # To maintain constant time across
        # all operations, maintain a dictionary
        # which tracks the index of each key stored
        # in `self.set`.
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
        """Force Eviction of Random item."""
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
        """Generate a random key from the cache."""
        return random.choice(self.set)


class VolatileRandomCache(VolatileCache):
    """Randomly evicts keys that are set to expire.

    Attributes:
        capacity (int): Maximum capacity of the cache.
        callback (callable, optional): Callable defining
        behaviour when an item is evicted from the cache.
        Defaults to None.
    """
    def __init__(self, capacity, callback=None):
        VolatileCache.__init__(self, capacity, callback)

        self._set = []
        # To maintain constant time across
        # all operations, maintain a dictionary
        # which tracks the index of each key stored
        # in `self.set`.
        self.idx_map = {}

    def __setitem__(self, _keymeta, _value):
        _key, expires = _keymeta

        VolatileCache.__setitem__(self, _keymeta, _value)
        if _key not in self.idx_map and expires:
            self._set.append(_key)
            self.idx_map[_key] = len(self._set) - 1

    def __delitem__(self, _key):
        VolatileCache.__delitem__(self, _key)
        # In order to perform a deletion without having
        # to iteratively decrement each element of `idx_map`,
        # we swap the last element of `set` with the element
        # to be deleted, and then pop the last element from `set`.
        if _key in self.idx_map:
            last_elem = self._set[-1]
            index = self.idx_map[_key]
            ssize = len(self._set) - 1

            if index < ssize:
                self._set[index] = last_elem
                self.idx_map[last_elem] = index

            self._set.pop()
            del self.idx_map[_key]

    def popitem(self):
        """Force Eviction of Random item."""
        try:
            _key = self.__get_rand_key()
        except:
            raise KeyError("cannot pop from empty cache") from None
        else:
            _val = VolatileCache.__getitem__(self, _key)
            del self[_key]
            return (_key, _val)

    def _evict(self):
        _key, _value = self.popitem()

        if self._callback:
            self._callback(_key, _value)

    def __get_rand_key(self):
        """Generate a random key from the cache.

        """
        return random.choice(self._set)


class TTLCache(LRUCache):
    """TTL cache with global object fixed expiry times.

    Monotonic time is used to track key expiry times.

    Attributes:
        capacity (int): Maximum capacity of the cache.
        ttl (int): Cache items time-to-live.
        callback (callable, optional): Callable defining
        behaviour when an item is evicted from the cache.
        Defaults to None.
        time (callable): Callable time function used by the
        cache.
    """
    def __init__(self, capacity, ttl, callback=None, _time=time.monotonic):
        LRUCache.__init__(self, capacity, callback)

        self._time = _time
        self.__ttl = ttl

        # Dict Mapping Keys to `_TTLLinks`
        # this is primarily used for O(1)
        # lookup and deletions of `_TTLLinks`
        self._links = {}

        # Linked List of '_TTLLinks'
        # The linked list is 'sorted' in time-ascending
        # order. The key with the nearest expiry time is
        # at the front of the list.
        self._list = _TTLLinkedList()

    def expire(_time):
        """Removes expired keys from the cache.

        Decorator for class methods. Iterates over the linked
        list and removes expired keys from the cache when
        the cache is accessed.
        """
        def wrap(func):

            def wrapped_f(self, *args):
                curr = self._list.head

                while curr:
                    if curr.expiry <= _time():
                        LRUCache.__delitem__(self, curr.key)
                        self._list.remove(curr)
                        del self._links[curr.key]
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
            link = self._links[_key]
        except KeyError:
            expiry = self._time() + self.__ttl
            self._links[_key] = link = _TTLLink(_key, expiry, None, None)
        else:
            self._list.remove(link)
            expiry = self._time() + self.__ttl
            link.expiry = expiry

        self._list.insert(link)

    @expire(_time=time.monotonic)
    def __getitem__(self, _key):
        try:
            _value = LRUCache.__getitem__(self, _key)
        except KeyError:
            raise KeyError(f"{_key}") from None
        else:
            return _value

    @expire(_time=time.monotonic)
    def get(self, _key, _default=None):
        try:
            return self[_key]
        except KeyError:
            return _default

    @expire(_time=time.monotonic)
    def __delitem__(self, _key):
        try:
            LRUCache.__delitem__(self, _key)
        except KeyError:
            raise KeyError(f"{_key}") from None
        else:
            link = self._links[_key]
            self._list.remove(link)
            del self._links[_key]

    @expire(_time=time.monotonic)
    def __contains__(self, _object: object):
        return RCache.__contains__(self, _object)

    @expire(_time=time.monotonic)
    def __iter__(self):
        return RCache.__iter__(self)

    @expire(_time=time.monotonic)
    def __len__(self):
        return RCache.__len__(self)

    def _evict(self):
        """Handle evictions when Cache exceeds capacity.
        Not time-related.

        Invokes callback function whenever an item is evicted.

        """
        # Fetch and Evict LRU Item from LRUCache
        _key, _value = LRUCache.popitem(self)

        # Remove References to Link
        link = self._links[_key]
        self._list.remove(link)
        del self._links[_key]

        if self._callback:
            self._callback(_key, _value)

    @expire(_time=time.monotonic)
    def __str__(self):
        return RCache.__repr__(self)

    def popitem(self):
        """Evict the LRU item."""
        # Fetch and Evict LRU Item from LRUCache
        _key, _value = LRUCache.popitem(self)

        # Remove References to Link
        link = self._links[_key]
        self._list.remove(link)
        del self._links[_key]

    # Enable 'expire' decorator to be accessed
    # outside of the scope of the class, while
    # still being inside the class namespace.
    expire = staticmethod(expire)


class VolatileTTLCache(VolatileLRUCache):
    """TTL Cache with Volatile Keys.

    Items with the expire field set to "True"
    are evicted from the cache. Items with the
    expire field set to "False" persist.

    Attributes:
        capacity (int): Maximum capacity of the cache.
        ttl (int): Cache items time-to-live.
        callback (callable, optional): Callable defining
        behaviour when an item is evicted from the cache.
        Defaults to None.
        time (callable): Callable time function used by the
        cache.
    """
    def __init__(self, capacity, ttl, callback=None, _time=time.monotonic):
        VolatileLRUCache.__init__(self, capacity, callback)

        self._time = _time
        self.__ttl = ttl

        # Dict Mapping Keys to `_TTLLinks`
        # this is primarily used for O(1)
        # lookup and deletions of `_TTLLinks`
        self._links = {}

        # Linked List of '_TTLLinks'
        # The linked list is 'sorted' in time-ascending
        # order. The key with the nearest expiry time is
        # at the front of the list.
        self._list = _TTLLinkedList()

    def expire(_time):
        """Removes expired keys from the cache.

        Decorator for class methods. Iterates over the linked
        list and removes expired keys from the cache when
        the cache is accessed.

        """
        def wrap(func):

            def wrapped_f(self, *args):
                curr = self._list.head

                while curr:
                    if curr.expiry <= _time():
                        VolatileLRUCache.__delitem__(self, curr.key)
                        self._list.remove(curr)
                        del self._links[curr.key]
                        curr = curr.next
                    else:
                        return func(self, *args)

                return func(self, *args)
            return wrapped_f
        return wrap

    @expire(_time=time.monotonic)
    def __setitem__(self, _keymeta, _value):
        _key, expires = _keymeta

        VolatileLRUCache.__setitem__(self, _keymeta, _value)
        try:
            link = self._links[_key]
        except KeyError:
            if expires:
                expiry = self._time() + self.__ttl
                self._links[_key] = link = _TTLLink(_key, expiry, None, None)
        else:
            self._list.remove(link)
            expiry = self._time() + self.__ttl
            link.expiry = expiry

        if expires:
            self._list.insert(link)

    @expire(_time=time.monotonic)
    def __getitem__(self, _key):
        try:
            _value = VolatileLRUCache.__getitem__(self, _key)
        except KeyError:
            raise KeyError(f"{_key}") from None
        else:
            return _value

    @expire(_time=time.monotonic)
    def get(self, _key, _default=None):
        try:
            return self[_key]
        except KeyError:
            return _default

    @expire(_time=time.monotonic)
    def __delitem__(self, _key):
        try:
            VolatileLRUCache.__delitem__(self, _key)
        except KeyError:
            raise KeyError(f"{_key}") from None
        else:
            if _key in self._links:
                link = self._links[_key]
                self._list.remove(link)
                del self._links[_key]

    @expire(_time=time.monotonic)
    def __contains__(self, _object: object):
        return VolatileLRUCache.__contains__(self, _object)

    @expire(_time=time.monotonic)
    def __iter__(self):
        return VolatileLRUCache.__iter__(self)

    @expire(_time=time.monotonic)
    def __len__(self):
        return VolatileCache.__len__(self)

    def _evict(self):
        """Handle evictions when Cache exceeds capacity.
        Not time-related.

        Invokes callback function whenever an item is evicted.

        """
        # Fetch and Evict LRU Item from LRUCache
        _key, _value = VolatileLRUCache.popitem(self)

        # Remove References to Link
        if _key in self._links:
            link = self._links[_key]
            self._list.remove(link)
            del self._links[_key]

        if self._callback:
            self._callback(_key, _value)

    @expire(_time=time.monotonic)
    def __str__(self):
        return VolatileLRUCache.__repr__(self)

    def popitem(self):
        """Evict the LRU item.

        """
        # Fetch and Evict LRU Item from LRUCache
        _key, _value = VolatileLRUCache.popitem(self)

        # Remove References to Link
        if _key in self._list:
            link = self._links[_key]
            self._list.remove(link)
            del self._links[_key]

    # Enable 'expire' decorator to be accessed
    # outside of the scope of the class, while
    # still being inside the class namespace.
    expire = staticmethod(expire)


class VTTLCache(TTLCache):
    """Variable time-to-live cache.

    Time-to-live cache with variable internal
    TTL's. TTL times are set per-item.

    Attributes:
        capacity (int): Maximum capacity of the cache.
        callback (callable, optional): Callable defining
        behaviour when an item is evicted from the cache.
        Defaults to None.
        time (callable): Callable time function used by the
        cache.
    """
    def __init__(self, capacity, callback=None, _time=time.monotonic):
        TTLCache.__init__(self, capacity, ttl=None, callback=callback, _time=_time)
        self.__rep = [] # List Representation of the Linked List

    @TTLCache.expire(_time=time.monotonic)
    def __setitem__(self, _keymeta, _value):
        _key, ttl = _keymeta

        LRUCache.__setitem__(self, _key, _value)
        try:
            link = self._links[_key]
        except KeyError:
            expiry = self._time() + ttl
            self._links[_key] = link = _TTLLink(_key, expiry, None, None)
        else:
            self._list.remove(link)
            self.__rep.remove(link)
            expiry = self._time() + ttl
            link.expiry = expiry # Update Expiry Time Before Re-Insertion

        self.__insert(link, expiry, _key)

    def _evict(self):
        """Handle evictions when Cache exceeds capacity.
        Not time-related.

        Invokes callback function whenever an item is evicted.

        """
        # Fetch and Evict LRU Item from LRUCache
        _key, _value = LRUCache.popitem(self)

        # Remove References to Link
        link = self._links[_key]
        self.__rep.remove(link)
        self._list.remove(link)
        del self._links[_key]

        if self._callback:
            self._callback(_key, _value)

    def __binary_search(self, expiry):
        """Binary searches the list of TTL nodes.

        Returns a tuple containing indexes used for insertion
        to the linked list and list representation.

        Args:
            expiry (int): item expiry time.

        Returns:
            int, int: Previous link reference index, list
            insertion reference index.
        """
        left = 0
        right = tail = len(self.__rep) - 1
        head = (0, 0)

        while left <= right:
            mid = (right + left) // 2

            if self.__rep[mid].expiry < expiry:
                if mid == tail:
                    return mid, mid + 1
                if self.__rep[mid + 1].expiry >= expiry:
                    return mid, mid + 1
                left += 1

            elif self.__rep[mid].expiry > expiry:
                if mid == 0:
                    return head
                if self.__rep[mid - 1].expiry <= expiry:
                    return mid, mid
                right -= 1

            else:
                return mid, mid

        return head

    def __insert(self, link, expiry, _key):
        """Handle Insertions of Link to the Linked List
        and List Representation.

        Args:
            link (_TTLLink): Link to insert.
            expiry (int): Expiry time.
            _key (hashable): Item Key.

        """
        node_index, list_index = self.__binary_search(expiry)

        if self.__rep:
            prev_link = self.__rep[node_index]
        else:
            prev_link = None

        self._list.sorted_insert(prev_link, link)
        self.__rep.insert(list_index, link)


class BoundedTTLCache(TTLCache):
    """TTL Cache with Random Bounded Expiry Times.

    Item TTL's are randomly generated between
    `ttl_min` and `ttl_max`. Range: [ttl_min, ttl_max].

    Attributes:
        capacity (int): Maximum capacity of the cache.
        ttl_min (int): TTL minimum value.
        ttl_max (int): TTL maximum value.
        callback (callable, optional): Callable defining
        behaviour when an item is evicted from the cache.
        Defaults to None.
        time (callable): Callable time function used by the
        cache.
    """
    def __init__(self, capacity, ttl_min, ttl_max, callback=None, _time=time.monotonic):
        TTLCache.__init__(self, capacity, None, callback, _time)
        # TTL Bounds
        self.ttl_min = ttl_min
        self.ttl_max = ttl_max

    @TTLCache.expire(_time=time.monotonic)
    def __setitem__(self, _key, _value):
        LRUCache.__setitem__(self, _key, _value)
        try:
            link = self._links[_key]
        except KeyError:
            ttl = random.randrange(self.ttl_min, self.ttl_max + 1)
            expiry = self._time() + ttl
            self._links[_key] = link = _TTLLink(_key, expiry, None, None)
        else:
            self._list.remove(link)
            ttl = random.randrange(self.ttl_min, self.ttl_max + 1)
            expiry = self._time() + ttl
            link.expiry = expiry

        self._list.insert(link)
