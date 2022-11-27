## RCache - Pure Python Cacheing Library


![Coverage](https://img.shields.io/codecov/c/github/breid48/rcache?token=E2GVMUS6KU)

### Performance

RCache offers 2-4x performance increases over Python's popular "Cachetools" library. The benchmark 
script referenced below is standardized in ./benchmark.py.

*Cache Maxsize=256, Num. Insertions=400

| Cache Type | OS | CPU | Cachetools | RCache |
| ------ | ----- | ----- | ------ | ----- |
| LRU | Windows 10 | Ryzen 5 5600H | 5.16302 | 2.89601 |
| LFU | Windows 10 | Ryzen 5 5600H | 19.5839 | 5.72118 |
| LRU | Ubuntu 20.04 | Ryzen 5 5600H | 4.4773 | 2.55951 |
| LFU | Ubuntu 20.04 | Ryzen 5 5600H | 17.9818 | 5.50492 |

*Cache Maxsize=512, Num. Insertions=600

| Cache Type | OS | CPU | Cachetools | RCache |
| ------ | ----- | ----- | ------ | ----- |
| LRU | Windows 10 | Ryzen 5 5600H | 8.63297 | 4.96194 |
| LFU | Windows 10 | Ryzen 5 5600H | 42.9374 | 9.84216 |
| LRU | Ubuntu 20.04 | Ryzen 5 5600H | 7.98137 | 4.38634 |
| LFU | Ubuntu 20.04 | Ryzen 5 5600H | 40.8033 | 9.71117 |

### Installation

```

pip install -U rcache

```

And then in your python interpreter:

```python

import rcache

```

### Updating

### Usage

```python

>>> from rcache import LFUCache

>>> cache = LFUCache(capacity=2)

>>> cache[1] = 2
>>> cache[2] = 3
>>> cache[3] = 4

>>> cache
LFUCache{2: 3, 3: 4}

```