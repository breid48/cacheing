import argparse
import importlib

from benchmark.cache_benchmark import CacheBenchmark
from benchmark.visualization import display


NUM_CACHES = 4


def initialize_parser() -> argparse.ArgumentParser:
    """Initialize parser object.

    Returns:
        argparse.ArgumentParser: Argument Parser.
    """
    parser = argparse.ArgumentParser(
                    prog = 'benchmark',
                    description = 'cache benchmarking tool')
    return parser


def parser_add_args(parser: argparse.ArgumentParser) -> argparse.ArgumentParser:
    parser.add_argument(
        "--cache", "-c",
        action='store',
        nargs='*',
        help='cache(s) to benchmark. example: rcache.LRUCache.'
    )
    parser.add_argument(
        "--method", "-m",
        choices=['get', 'set', 'delete'],
        action='store',
        nargs='*',
        help='method(s) to benchmark.'
    )

    return parser


def process_args(parser: argparse.ArgumentParser):
    """Process command-line arguments.

    Args:
        parser (argparse.ArgumentParser): Argument Parser.

    Returns:
        tuple(list, set): List of caches, set of methods.
    """
    classes = []

    args = parser.parse_args()

    if args.cache:
        for arg in args.cache:
            _object = wrapped_import(arg)
            classes.append(_object)

    methods = args.method if args.method else None

    return classes, methods


def wrapped_import(module_class_descriptor):
    """Import a class object given a string descriptor.

    Args:
        module_class_descriptor (str): Desired import.
        Form: module.class. Ex: cachetools.LRUCache

    Returns:
         object: Class Object.
    """
    str_module, str_class = module_class_descriptor.split(".")
    module = importlib.import_module(str_module)
    _class = getattr(module, str_class)

    return _class


def generate_caches(classes: list):
    """Generate `n=NUM_CACHES` caches for each
    cache defined in `classes`.

    By default (bit_mask = 256 and NUM_CACHES = 4),
    this function generates a set of caches with capacities:

        {256, 1024, 4096, 16384}

    For each cache in `classes`.

    Args:
        classes (list): List of cache classes to build.

    Returns:
        dict: Dict mapping UID's to Cache's.
    """
    caches = {}

    for _class in classes:
        mask = 256  # Bit-Mask

        for _ in range(NUM_CACHES):
            # uid = f"{_class.__module__}.{_class.__name__}.{mask}"
            package_class_id = f"{_class.__module__}.{_class.__name__}"
            _object = _class(mask)
            if package_class_id not in caches:
                caches[package_class_id] = {}
            caches[package_class_id][mask] = _object
            mask <<= 2

    return caches


def generate_benchmarks(caches: dict, methods: list):
    """Wrap Cache objects in the `CacheBenchmark` class.

    Args:
        caches (dict): Dictionary of uids:cache_objects.

    Returns:
        dict: Dictionary of uids:benchmark_objects.
    """
    for package_class_id, c_map in caches.items():
        for c_size, cache in c_map.items():
            c_map[c_size] = CacheBenchmark(cache=cache, methods=methods)

    return caches


def compile_benchmarks(caches: dict):
    """Run the benchmarks. """
    for package_class_id, c_map in caches.items():
        for c_size, _object in c_map.items():
            _object.compile()

    return caches


arg_parser = initialize_parser()
parser_add_args(arg_parser)
cls, mth = process_args(arg_parser)

cache_map = generate_caches(cls)
cache_map = generate_benchmarks(cache_map, mth)
results = compile_benchmarks(cache_map)
display(results)