import polars as pl
from typing import Callable
from sklearn.utils.extmath import cartesian
from concurrent.futures import ProcessPoolExecutor
import matplotlib.pyplot as plt
import numpy as np

class Fastlyzer:
    def __init__(self, 
                 f: Callable,
                 cache_file_name: str = "fastlyze_cache.csv",
                 input_schema: list = [],
                 output_schema: list = []):
        self.f = f
        self.cache_file_name = cache_file_name
        self.input_schema = input_schema
        self.output_schema = output_schema
        self.merged_schema = [*input_schema, *output_schema]
        self.cache_table = self._get_chashed_table()

    def _get_chashed_table(self) -> pl.DataFrame:
        try:
            return pl.read_csv(self.cache_file_name)
        except:
            print("cache not found")
        return pl.DataFrame([], schema=self.merged_schema)
    
    def _gen_param_table(self, params: dict) -> pl.DataFrame:
        param_list_list = []
        for key, _ in self.input_schema:
            if key not in params:
                raise ValueError(f"Missing key: {key}")
            param = params[key]
            param_list_list.append(param if isinstance(param, list) else [param])
        param_list = cartesian(param_list_list)
        param_table = pl.DataFrame(param_list, schema=self.input_schema)
        return param_table

    def run(self, params: dict):
        target_table = self._gen_param_table(params)
        input_keys = list(params.keys())
        merged_table = target_table.join(self.cache_table, on=input_keys, how="left")

        no_cache_params = merged_table.filter(pl.col(self.output_schema[0][0]).is_null())
        print(f"{len(no_cache_params)}/{merged_table.shape[0]} params are not cached")
        if len(no_cache_params) == 0:
            return merged_table
        
        futures = []
        with ProcessPoolExecutor(max_workers=6) as executor:
            for param in no_cache_params.drop(*[col[0] for col in self.output_schema]).to_dicts():
                futures.append(executor.submit(self.f, **param))
        result_dict = {col[0]: [] for col in self.output_schema}
        for future in futures:
            result = future.result()
            for key, value in result.items():
                result_dict[key].append(value)

        updated_table = no_cache_params.with_columns([
            pl.Series(col, value) for col, value in result_dict.items()
        ])

        self.cache_table = pl.concat([
            self.cache_table,
            updated_table
        ])
        self.cache_table.write_csv(self.cache_file_name)

    
    def visualize(self, 
                  x_col: str, 
                  y_col: str, 
                  by_col: str,
                  const_cols: dict):
        table = self.cache_table
        table = table.filter(**const_cols).select(pl.col("*").sort_by(x_col))

        # visualize
        fig, axs = plt.subplots(1, 1, figsize=(10, 10))
        axs = axs if isinstance(axs, np.ndarray) else [axs]
        for group_key, sub_table in table.group_by([by_col]):
            axs[0].plot(sub_table[x_col], sub_table[y_col], label=f"{by_col}={group_key}")
        axs[0].set_title(f"{y_col} vs {x_col}")
        axs[0].set_xlabel(x_col)
        axs[0].set_ylabel(y_col)
        axs[0].legend()
        plt.show()
