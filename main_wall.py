from fastlyze import Fastlyzer
from calculation import calculation

import numpy as np
import polars as pl
import matplotlib.pyplot as plt
def main():
    fastlyzer = Fastlyzer(
        f=calculation,
        cache_file_name="cache0531.csv",
        input_schema=[
            ("pulse_num", pl.Int64),
            ("min_interval_ns", pl.Int64),
            ("max_interval_ns", pl.Int64),
            ("max_torelance_error_ns", pl.Int64),
            ("consider_amp", pl.Boolean),
            ("min_amp_diff_ratio", pl.Float64),
            ("max_amp_diff_ratio", pl.Float64),
            ("max_amp_torelance_error", pl.Float64),
            ("outdoor_wall_distance_m", pl.Float64),
            ("outdoor_wall_reflectivity", pl.Float64),
            ("spoofer_frequency_mhz", pl.Float64),
            ("spoofer_pulse_width_ns", pl.Int64),
            ("noise_ratio", pl.Float64),
        ],
        output_schema=[
            ("ASR", pl.Float64),
            ("Lost Point Rate", pl.Float64),
        ]
    )

    fastlyzer.run({
        "pulse_num": [2],
        "min_interval_ns": [250],
        "max_interval_ns": [450],
        "max_torelance_error_ns": [20],
        "consider_amp": [True],
        "min_amp_diff_ratio": [0.2],
        "max_amp_diff_ratio": [0.4],
        "max_amp_torelance_error": [0.05],
        "outdoor_wall_distance_m": [10.0, 30.0, 50.0, 70.0, 90.0, 110.0],
        "outdoor_wall_reflectivity": [0.1, 0.3, 0.5, 0.7, 0.9],
        "spoofer_frequency_mhz": [25.0],
        "spoofer_pulse_width_ns": [5],
        "noise_ratio": [0.01],
    })

    result_table = fastlyzer.cache_table.filter(
        pulse_num=2,
        min_interval_ns=250,
        max_interval_ns=450,
        max_torelance_error_ns=20,
        consider_amp=True,
        min_amp_diff_ratio=0.2,
        max_amp_diff_ratio=0.4,
        max_amp_torelance_error=0.05,
        # outdoor_wall_distance_m=50.0,
        # outdoor_wall_reflectivity=0.8,
        spoofer_frequency_mhz=25.0,
        spoofer_pulse_width_ns=5,
        noise_ratio=0.01,
    )

    x_col = "outdoor_wall_distance_m"
    y_col = "outdoor_wall_reflectivity"
    pivot = result_table.pivot(
        index=y_col,
        columns=x_col,
        values="ASR"
    ).select(pl.col("*").sort_by([y_col]))
    pivot = pivot[
        [y_col] + [str(x) for x in sorted([float(col) for col in pivot.columns if col != y_col])]
    ]
    print(pivot)

    plt.imshow(pivot.to_numpy()[:,1:], cmap="jet", interpolation="none")
    plt.colorbar()
    plt.xlabel(x_col)
    plt.ylabel(y_col)
    plt.xticks(range(len(pivot.columns[1:])), pivot.columns[1:])
    plt.yticks(range(len(pivot[y_col])), pivot[y_col].to_list())
    plt.show()

if __name__ == "__main__":
    main()
