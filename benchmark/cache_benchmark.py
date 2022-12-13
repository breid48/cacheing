import time
import random
import statistics

import numpy as np


NITERATIONS = 100000 # Number of Get & Delete operations
NSETS = 20000 # Number of Sets. Ensure NSETS > max cache size to simulate evictions.


class CacheBenchmark:
    """Benchmark Encapsulation.

    Attributes:
        cache (object): Cache object implementing `__getitem__`, `__setitem__`
        and `__delitem__` methods. The cache should also expose it's internal
        `maxsize` or `capacity` attribute.

    """
    def __init__(self, cache, methods: list=None):
        required = ["__getitem__", "__setitem__", "__delitem__"]
        for func in required:
            attr = getattr(cache, func, None)
            if not callable(attr):
                raise AttributeError(f"{cache.__class__} does not implement {func}.")

        self.capacity = None
        options = ["capacity", "maxsize"]
        for option in options:
            if hasattr(cache, option):
                self.capacity = getattr(cache, option, None)
        if not self.capacity:
            raise AttributeError(f"{cache.__class__} does not expose `maxsize` or `capacity`.")

        self._results = {
                        "get": [],
                        "set": [],
                        "delete": []
                        }

        self._statistics = {
                        "get": {},
                        "set": {},
                        "delete": {}
                        }

        self._cache = cache

        self._methods = methods
        if not methods:
            self._methods = ["get", "set", "delete"]

    @property
    def results(self):
        return self._results

    @property
    def statistics(self):
        return self._statistics

    @property
    def cache(self):
        return self._cache

    def compile(self):
        """Runs selected benchmarks and compiles statistics.

        """
        mmap = {"get": self._gets,
                "set": self._sets,
                "delete": self._deletes
                }

        for method in self._methods:
            func = mmap[method]
            results = func()
            self._results[method].extend(results)

        self._generate_statistics()

    def _generate_statistics(self):
        """Generate statistics from cache run-times.

        self._statistics:
            {
            "median": None,
            "p90": None,
            "p99": None,
            "std": None,
            "var": None
            }
        """
        for operation, results in self._results.items():
            if results:
                self._statistics[operation]["median"] = statistics.median(results)
                self._statistics[operation]["p90"] = np.percentile(results, 90)
                self._statistics[operation]["p99"] = np.percentile(results, 99)
                self._statistics[operation]["std"] = statistics.stdev(results)
                self._statistics[operation]["var"] = statistics.variance(results)

    def _gets(self, number=NITERATIONS):
        """Benchmark `get` operations.

        Args:
            number (int, optional): Number of iterations.
            Defaults to NITERATIONS.

        """
        times = []

        cache_size = self.capacity

        # Populate Cache with Random Values
        for key in range(cache_size):
            self.cache[key] = key + 1

        for _ in range(number):
            key = random.randrange(cache_size)
            start = time.perf_counter()
            val = self.cache[key]
            end = time.perf_counter()
            elapsed = end - start

            times.append(elapsed)

        return times

    def _sets(self, number=NSETS):
        """Benchmark `set` operations.

        Args:
            number (int, optional): Number of iterations.
            Defaults to NITERATIONS.

        Returns:
            _type_: _description_
        """
        times = []

        for key in range(number):
            value = key + 1
            start = time.perf_counter()
            self.cache[key] = value
            end = time.perf_counter()
            elapsed = end - start

            times.append(elapsed)

        return times

    def _deletes(self):
        """Benchmark `delete` operations.

        Args:
            number (int, optional): Number of iterations.
            Defaults to NITERATIONS.

        Returns:
            _type_: _description_
        """
        times = []

        cache_size = self.capacity

        # Populate Cache
        for i in range(cache_size):
            self.cache[i] = i + 1

        for key in range(cache_size):
            start = time.perf_counter()
            del self.cache[key]
            end = time.perf_counter()
            elapsed = end - start

            times.append(elapsed)

        return times
