import pandas as pd


def build_dataframe(results: dict):
    """Constructs dataframe from transformed data.

    Args:
        results (dict): Transformed data yielded from `transform_data()`.
    """
    bar_chart_data = {"set": [], "get": [], "delete": []}

    for cache_name, data in results.items():
        cache_type = cache_name.split(".")[-1]
        library = cache_name.rsplit(".",1)[0]
        for cache_size, statistics in data.items():
            for method, stats in statistics.items():
                if stats:
                    bar_chart_entry = {"library": library, 
                                       "cache_type": cache_type,
                                       "cache_size": cache_size,
                                       "median": stats["median"],
                                       "p90": stats["p90"],
                                       "p99": stats["p99"]}
                    bar_chart_data[method].append(bar_chart_entry)

    df_set = pd.DataFrame.from_dict(bar_chart_data["set"])
    df_get = pd.DataFrame.from_dict(bar_chart_data["get"])
    df_delete = pd.DataFrame.from_dict(bar_chart_data["delete"])

    print("Get: \n", df_set)
    print("Set: \n", df_get)
    print("Delete: \n", df_delete)


def transform_data(cache_results: dict):
    """Normalize values to microseconds (1 millionth of a second).

    Args:
        cache_results (dict): Cache results yielded from
        `benchmark.compile_benchmarks()`.
    """
    transformed_data = {}

    for cache_type, cache_map in cache_results.items():
        transformed_data[cache_type] = {}
        for cache_size, cache_object in cache_map.items():
            transformed_data[cache_type][cache_size] = {"get": {}, "set": {}, "delete": {}}
            for method, stat_sum in cache_object.statistics.items():
                inner = {stat_name: stat*1000000 for stat_name, stat in stat_sum.items()}
                transformed_data[cache_type][cache_size][method] = inner

    return transformed_data


def display(cache_results: dict):
    """_summary_

    Args:
        cache_results (dict): _description_
    """
    transformed_results = transform_data(cache_results=cache_results)
    build_dataframe(transformed_results)
