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
        "pulse_num": [1,2,3],
        "min_interval_ns": [250],
        "max_interval_ns": [450],
        "max_torelance_error_ns": [20],
        "consider_amp": [True, False],
        "min_amp_diff_ratio": [0.2],
        "max_amp_diff_ratio": [0.4],
        "max_amp_torelance_error": [0.05],
        "outdoor_wall_distance_m": [50.0],
        "outdoor_wall_reflectivity": [0.8],
        "spoofer_frequency_mhz": np.arange(0.0, 30.1, 3.0).tolist(),
        "spoofer_pulse_width_ns": [5],
        "noise_ratio": [0.01],
    })

    result_table = fastlyzer.cache_table.filter(
        # pulse_num=2,
        min_interval_ns=250,
        max_interval_ns=450,
        max_torelance_error_ns=20,
        # consider_amp=True,
        min_amp_diff_ratio=0.2,
        max_amp_diff_ratio=0.4,
        max_amp_torelance_error=0.05,
        outdoor_wall_distance_m=50.0,
        outdoor_wall_reflectivity=0.8,
        # spoofer_frequency_mhz=0.0,
        spoofer_pulse_width_ns=5,
        noise_ratio=0.01,
    ).select(pl.col("*").sort_by("spoofer_frequency_mhz"))

    for pulse_num, consider_amp in [[1, False], [2, False], [3, False], [2, True]]:
        selected = result_table.filter(pulse_num=pulse_num, consider_amp=consider_amp)
        plt.plot(selected["spoofer_frequency_mhz"], selected["ASR"], label=f"pulse_num={pulse_num}, consider_amp={consider_amp}")
    plt.xlabel("Spoofer Frequency (MHz)")
    plt.ylabel("ASR")
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()
