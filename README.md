## cacheing - Pure Python Cacheing Library

---

![Coverage](https://img.shields.io/codecov/c/github/breid48/rcache?token=E2GVMUS6KU)

### Resources

- [Installation](#Installation)
- [Updating](#Updating)
- [Basic Usage](#basic-usage)
- [Benchmark](#Benchmark)
- [Performance](#Performance)
- [Callback Functions](#callback-functions)

### Supported Caches
- [LFUCache](#LFUCache)
- [LRUCache](#LRUCache)
- [VolatileCache(s)](#VolatileCaches)
- [TTLCache](#TTLCache)
- [VTTLCache](#VTTLCache)
- [RandomCache](#RandomCache)

---

### Motivation

---

The initial motivation behind this package was twofold: fix the long insertion/eviction times in `cachetools.LFUCache` and provide an alternative to the `cachetools.TTLCache` offering variable per-key TTL's.


### Installation

---

```
pip install cacheing
```

And then in your python interpreter:

```python
import cacheing
```

### Updating

---
```
pip install -U cacheing
```




### Basic Usage

---

```python
from cacheing import LFUCache

cache = LFUCache(capacity=2)

cache[1] = 2
cache[2] = 3
cache[3] = 4

>>> cache
LFUCache{2: 3, 3: 4}
```

### Benchmark

---

cacheing provides a benchmarking library found in `./benchmark`.

```shell
$ python3 ./benchmark.py --help

usage: benchmark [-h] [--cache [CACHE [CACHE ...]]] [--method [{get,set,delete} [{get,set,delete} ...]]]

arguments:
  -h, --help            show this help message and exit
  --cache [CACHE [CACHE ...]], -c [CACHE [CACHE ...]]
                        cache(s) to benchmark. example: cacheing.LRUCache.
  --method [{get,set,delete} [{get,set,delete} ...]], -m [{get,set,delete} [{get,set,delete} ...]]
                        method(s) to benchmark.
```

#### Run the Benchmarks:
```shell
$ cd benchmark

$ python3 ./benchmark.py --cache cachetools.LRUCache cacheing.LRUCache --method set get delete
```


### Performance

--- 
All benchmark times were measured using the provided `benchmark` library. See the
[benchmark section](#Benchmark) for details. The default benchmarking configuration executes 100,000 get operations, 
20,000 set operations and `n = cache_size` delete operations. The median, p90, and p99 times for each
operation, measured in microseconds, or `1e-6`, are displayed in the figures below.


#### Get (LFU Cache)  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;            Delete (LFU Cache)

<img src="https://raw.githubusercontent.com/breid48/cacheing/main/assets/lfu_get.png" width="300"> <img src="https://raw.githubusercontent.com/breid48/cacheing/main/assets/lfu_delete.png" width="300">

####    Set (LFU Cache) &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;            Set - Cross Section (LFU Cache)

<img src="https://raw.githubusercontent.com/breid48/cacheing/main/assets/lfu_set.png" width="300"> <img src="https://raw.githubusercontent.com/breid48/cacheing/main/assets/lfu_set_crosssection.png" width="300">

---

####    Set (LRU Cache)  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;            Get (LRU Cache)

<img src="https://raw.githubusercontent.com/breid48/cacheing/main/assets/lru_set.png" width="300"> <img src="https://raw.githubusercontent.com/breid48/cacheing/main/assets/lru_get.png" width="300">

#### Delete (LRU Cache)

<img src="https://raw.githubusercontent.com/breid48/cacheing/main/assets/lru_delete.png" width="300">


### Callback Functions

---

A callback function can be specified in the body of each cache constructor. The callback function is automatically invoked when an
item is evicted from the cache. The callback function signature should take two arguments mapping to the `key` and `value` of the evicted
item.

```python
import datetime

from cacheing import LFUCache

# Define a Callback-Function
def _cache_log(key, value):
    print(f"<{datetime.now()}> [Evict] {{{key}: {value}}}")

# Register Callback in the cache constructor
cache = LFUCache(capacity=2, callback=_cache_log)

cache[1] = 2
cache[2] = 3
cache[1]  # Get
cache[2]  # Get
cache[3] = 4

>>> cache
<2023-01-09 21:52:11.109161> [Evict] {1: 2}
LFUCache{2: 3, 3: 4}

```

### LFUCache

---
Evictions are performed using a "Least Frequently Used" eviction policy. Cache items are "ranked" based on their overall usage. When the cache
is at capacity and a request is made to insert a new item, the item with the least overall usage is evicted. 

Usage is tracked by-key. Gets and Sets are considered usage qualifiers.

See: [LFU Benchmarks](#Performance)
```python
from cacheing import LFUCache

cache = LFUCache(capacity=2)

cache[1] = 2
cache[2] = 3
cache[1]  # Get
cache[2]  # Get
cache[3] = 4

>>> cache
LFUCache{2: 3, 3: 4}
```

### LRUCache

---
Evictions are performed using a "Least Recently Used" eviction policy. Cache items are "ranked" based on how recently they were used. This is the 
reccomended cache to use when your data has high locality. When the cache
is at capacity and a request is made to insert a new item, the least-recently accessed item is evicted. 

Usage is tracked by-key. Gets and Sets are considered usage qualifiers.

See: [LRU Benchmarks](#Performance)
```python
from cacheing import LRUCache

cache = LRUCache(capacity=2)

cache[1] = 2
cache[2] = 3
cache[2]  # Get
cache[1]  # Get
cache[3] = 4

>>> cache
LRUCache{1: 2, 3: 4}
```

### VolatileCaches

---
VolatileCache's are inspired by the Redis API's of the same name. See [Redis Eviction Policies](https://redis.io/docs/reference/eviction/). 

VolatileCache's are variants of LFU, LRU, Random, and TTL Cache's offering optional item eviction. Specific cache items can be held in-memory
by setting their unique `expire` fields to `False`.

Volatile variant supported:

- `VolatileLFUCache`
- `VolatileLFUCache`
- `VolatileTTLCache`
- `VolatileRandomCache`
```python
from cacheing import VolatileLRUCache

cache = VolatileLRUCache(capacity=2)

cache[1, False] = 2
cache[2, False] = 3
cache[3, True] = 4

>>> cache
VolatileLRUCache{1: 2, 2: 3}

```

### TTLCache

---
TTLCache is a time-aware cache implementation. The `ttl` field defines the global time-to-live binding each item in the 
cache. The cache uses an underlying `LRUCache` to handle evictions. When the cache is at capacity and a request 
is made to insert a new item, the least recently used item is evicted.

```python
import asyncio
from cacheing import TTLCache

cache = TTLCache(capacity=2, ttl=5)

cache[1] = 2
cache[2] = 3

asyncio.sleep(5) # Some task

cache[3] = 4

>>> cache
TTLCache{3: 4}
```

### VTTLCache

---
Like [TTLCache](#TTLCache), VTTLCache is a time-aware cache implementation. Time to lives are explicitly assigned per-key. The cache uses an underlying `LRUCache` to handle evictions. When the cache is at capacity and a request 
is made to insert a new item, the least recently used item is evicted.

```python
import asyncio
from cacheing import VTTLCache

cache = VTTLCache(capacity=2)

# cache[key, ttl] = value
cache[1, 5] = 2
cache[2, 6] = 3

asyncio.sleep(5) # Some task

cache[3, 5] = 4

>>> cache
VTTLCache{2: 3, 3: 4}
```

### RandomCache

---
Randomly select an item for eviction.

```python
from cacheing import RandomCache

cache = RandomCache(capacity=2)

cache[1] = 2
cache[2] = 3
cache[1]  # Get
cache[2]  # Get
cache[3] = 4

>>> cache
RandomCache{1: 2, 3: 4}
```
