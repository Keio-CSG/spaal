from fastlyze import Fastlyzer
from calculation import calculation

import numpy as np
import polars as pl
import matplotlib.pyplot as plt
def main():
    fastlyzer = Fastlyzer(
        f=calculation,
        cache_file_name="cache0701.csv",
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
            ("sunlight_level", pl.Float64),
            ("thd_factor", pl.Float64),
        ],
        output_schema=[
            ("ASR", pl.Float64),
            ("Lost Point Rate", pl.Float64),
        ]
    )

    # fastlyzer.run({
    #     "pulse_num": [1,2],
    #     "min_interval_ns": [250],
    #     "max_interval_ns": [450],
    #     "max_torelance_error_ns": [20],
    #     "consider_amp": [False],
    #     "min_amp_diff_ratio": [0.2],
    #     "max_amp_diff_ratio": [0.4],
    #     "max_amp_torelance_error": [0.05],
    #     "outdoor_wall_distance_m": [50.0],
    #     "outdoor_wall_reflectivity": [0.8],
    #     "spoofer_frequency_mhz": [0.0, 10.0, 30.0],
    #     "spoofer_pulse_width_ns": [5],
    #     "noise_ratio": [0.01],
    #     "sunlight_level": [0.0, 0.5, 1.0, 1.5, 2.0],
    #     "thd_factor": [1.0],
    # })
    fastlyzer.run({
        "pulse_num": [1, 2],
        "min_interval_ns": [250],
        "max_interval_ns": [450],
        "max_torelance_error_ns": [20],
        "consider_amp": [True],
        "min_amp_diff_ratio": [0.2],
        "max_amp_diff_ratio": [0.4],
        "max_amp_torelance_error": [0.05],
        "outdoor_wall_distance_m": [50.0],
        "outdoor_wall_reflectivity": [0.8],
        "spoofer_frequency_mhz": [0.0, 10.0, 30.0],
        "spoofer_pulse_width_ns": [5],
        "noise_ratio": [0.01],
        "sunlight_level": [0.0, 0.5, 1.0, 1.5, 2.0],
        "thd_factor": [1.0],
    })
    fastlyzer.run({
        "pulse_num": [1, 2],
        "min_interval_ns": [250],
        "max_interval_ns": [450],
        "max_torelance_error_ns": [20],
        "consider_amp": [True],
        "min_amp_diff_ratio": [0.2],
        "max_amp_diff_ratio": [0.4],
        "max_amp_torelance_error": [0.05],
        "outdoor_wall_distance_m": [50.0],
        "outdoor_wall_reflectivity": [0.8],
        "spoofer_frequency_mhz": [0.0, 10.0, 30.0],
        "spoofer_pulse_width_ns": [5],
        "noise_ratio": [0.01],
        "sunlight_level": [0.0, 0.5, 1.0, 1.5, 2.0],
        "thd_factor": [0.0],
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
        outdoor_wall_distance_m=50.0,
        outdoor_wall_reflectivity=0.8,
        # spoofer_freqnency_mhz=0.0,
        spoofer_pulse_width_ns=5,
        noise_ratio=0.01,
        # sunlight_level=0.0,
        thd_factor=0.0
    )

    for freq in [0.0, 10.0, 30.0]:
        selected = result_table.filter(spoofer_frequency_mhz=freq)
        plt.plot(selected["sunlight_level"], selected["ASR"], label=f"spoofer_frequency_mhz={freq}")

    plt.xlabel("Sunlight Level")
    plt.ylabel("ASR")
    plt.ylim(0, 1)
    plt.legend()
    plt.show()

if __name__ == "__main__":
    main()
