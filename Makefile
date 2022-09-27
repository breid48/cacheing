test:
	python3 -m unittest discover -p 'test_*.py'

test-rcache:
	python3 -m unittest tests/test_rcache.py

test-lru:
	python3 -m unittest tests/test_lru_cache.py

test-lfu:
	python3 -m unittest tests/test_lfu_cache.py

test-random:
	python3 -m unittest tests/test_random_cache.py

test-ttl:
	python3 -m unittest tests/test_ttl_cache.py

test-volatile:
	python3 -m unittest tests/test_volatile_cache.py