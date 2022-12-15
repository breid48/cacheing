## cacheing - Pure Python Cacheing Library


![Coverage](https://img.shields.io/codecov/c/github/breid48/rcache?token=E2GVMUS6KU)

---

### Motivation

---

The initial motivation behind this package was twofold: fix the long insertion/eviction times in `cachetools.LFUCache` and provide an alternative to the `cachetools.TTLCache` offering variable per-key TTL's.


### Installation

---

```
pip install -U cacheing
```

And then in your python interpreter:

```python
import cacheing
```

### Updating

---



### Usage

---

```python
>>> from cacheing import LFUCache

>>> cache = LFUCache(capacity=2)

>>> cache[1] = 2
>>> cache[2] = 3
>>> cache[3] = 4

>>> cache
LFUCache{2: 3, 3: 4}
```

### Benchmark

---

cacheing has an included benchmarking library found in `./benchmark`.

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

---

####    Get (LFU Cache)  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;            Delete (LFU Cache)

<img src="https://raw.githubusercontent.com/breid48/cacheing/main/assets/lfu_get.png" width="300"> <img src="https://raw.githubusercontent.com/breid48/cacheing/main/assets/lfu_delete.png" width="300">

####    Set (LFU Cache) &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;            Set - Cross Section (LFU Cache)

<img src="https://raw.githubusercontent.com/breid48/cacheing/main/assets/lfu_set.png" width="300"> <img src="https://raw.githubusercontent.com/breid48/cacheing/main/assets/lfu_set_crosssection.png" width="300">

---

####    Set (LRU Cache)  &emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;&emsp;            Get (LRU Cache)

<img src="https://raw.githubusercontent.com/breid48/cacheing/main/assets/lru_set.png" width="300"> <img src="https://raw.githubusercontent.com/breid48/cacheing/main/assets/lru_get.png" width="300">

#### Delete (LRU Cache)

<img src="https://raw.githubusercontent.com/breid48/cacheing/main/assets/lru_delete.png" width="300">
