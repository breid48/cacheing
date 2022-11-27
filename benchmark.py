import timeit
from tabulate import tabulate

def benchmark(cache):
    """Benchmark a cache.

    This benchmark performs:
    - 400 Cache Insertions
    - 656 Total Operations to Re-Position the LRU/LFU Ordering
    - 144 Cache Evictions using the Cache Eviction Policy (LRU/LFU)
    - 256 Cache Deletions
    """
    for i in range(400):
        cache[i] = i + 1
    
    for key in list(cache.keys()):
        del cache[key]


cachetools_lru = timeit.timeit("benchmark(cache)", setup=("from cachetools import LRUCache;"
                                                         "from __main__ import benchmark;"
                                                         "cache=LRUCache(maxsize=256)"), number=10000)

cachetools_lfu = timeit.timeit("benchmark(cache)", setup=("from cachetools import LFUCache;"
                                                         "from __main__ import benchmark;"
                                                         "cache=LFUCache(maxsize=256)"), number=10000)

rcache_lru = timeit.timeit("benchmark(cache)", setup=("from src.rcache import LRUCache;"
                                                         "from __main__ import benchmark;"
                                                         "cache=LRUCache(capacity=256)"), number=10000)

rcache_lfu = timeit.timeit("benchmark(cache)", setup=("from src.rcache import LFUCache;"
                                                         "from __main__ import benchmark;"
                                                         "cache=LFUCache(capacity=256)"), number=10000)

table = [["LRU", cachetools_lru, rcache_lru], ["LFU", cachetools_lfu, rcache_lfu]]
print(tabulate(table, headers = ["Cache Type", "Cachetools", "RCache"], tablefmt="outline"))

