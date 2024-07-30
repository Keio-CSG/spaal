from spaal2 import DummyLidarSony, DummyOutdoor, DummySpooferContinuousPulse, DummySpooferOff, PreciseDuration, apply_noise
from fastlyze import Fastlyzer
import time
from concurrent.futures import ProcessPoolExecutor
from multiprocessing import get_context
from typing import Optional, Callable, Union, Tuple, List

import matplotlib.pyplot as plt
import numpy as np
from sklearn.utils.extmath import cartesian
import polars as pl

def calculation(
        pulse_num: int,
        min_interval_ns: int,
        max_interval_ns: int,
        max_torelance_error_ns: int,
        consider_amp: bool,
        max_amp_diff_ratio: float,
        max_amp_torelance_error: float,
        outdoor_wall_distance_m: float,
        outdoor_wall_reflectivity: float,
        spoofer_frequency_mhz: float,
        spoofer_pulse_width_ns: int,
        noise_ratio: float,
):
    print(f"spoofer_frequency_mhz: {spoofer_frequency_mhz}MHz, pulse_num: {pulse_num}, consider_amp: {consider_amp}, noise_ratio: {noise_ratio}")
    lidar = DummyLidarSony(
        pulse_num=pulse_num,
        min_interval=PreciseDuration(nanoseconds=250),
        max_interval=PreciseDuration(nanoseconds=450),
        max_torelance_error=PreciseDuration(nanoseconds=20),
        consider_amp=consider_amp,
        max_amp_diff_ratio=0.4,
        max_amp_torelance_error=0.05,
    )
    outdoor = DummyOutdoor(50.0, 0.8)
    if spoofer_frequency_mhz == 0:
        spoofer = DummySpooferOff()
    else:
        spoofer = DummySpooferContinuousPulse(frequency=spoofer_frequency_mhz*1e6, pulse_width=PreciseDuration(nanoseconds=5))

    point_list = []
    while True:
        try:
            config, signal = lidar.scan()

            signal = apply_noise(outdoor.apply(signal), ratio=noise_ratio)
            signal += apply_noise(spoofer.get_range_signal(config.start_timestamp, config.accept_duration), ratio=noise_ratio)
            signal = np.clip(signal, 0, 9)
            points, echoes = lidar.receive(config, signal)
            point_list.extend(points)
        except StopIteration:
            break

    max_point_num = lidar.max_index
    available_point_num = len(point_list)
    remain_point_num = len([x for x in point_list if x.distance_m > 49.5 and x.distance_m < 50.5])
    return {
        "ASR": 1 - remain_point_num / max_point_num, 
        "Lost Point Rate": 1 - available_point_num / max_point_num
    }

def generate_param_list(
        pulse_num: Union[List[int], int],
        min_interval_ns: Union[List[int], int],
        max_interval_ns: Union[List[int], int],
        max_torelance_error_ns: Union[List[int], int],
        consider_amp: Union[List[bool], bool],
        max_amp_diff_ratio: Union[List[float], float],
        max_amp_torelance_error: Union[List[float], float],
        outdoor_wall_distance_m: Union[List[float], float],
        outdoor_wall_reflectivity: Union[List[float], float],
        spoofer_frequency_mhz: Union[List[float], float],
        spoofer_pulse_width_ns: Union[List[int], int],
        noise_ratio: Union[List[float], float]) -> pl.DataFrame:
    param_list_list = [
        pulse_num if isinstance(pulse_num, list) else [pulse_num],
        min_interval_ns if isinstance(min_interval_ns, list) else [min_interval_ns],
        max_interval_ns if isinstance(max_interval_ns, list) else [max_interval_ns],
        max_torelance_error_ns if isinstance(max_torelance_error_ns, list) else [max_torelance_error_ns],
        consider_amp if isinstance(consider_amp, list) else [consider_amp],
        max_amp_diff_ratio if isinstance(max_amp_diff_ratio, list) else [max_amp_diff_ratio],
        max_amp_torelance_error if isinstance(max_amp_torelance_error, list) else [max_amp_torelance_error],
        outdoor_wall_distance_m if isinstance(outdoor_wall_distance_m, list) else [outdoor_wall_distance_m],
        outdoor_wall_reflectivity if isinstance(outdoor_wall_reflectivity, list) else [outdoor_wall_reflectivity],
        spoofer_frequency_mhz if isinstance(spoofer_frequency_mhz, list) else [spoofer_frequency_mhz],
        spoofer_pulse_width_ns if isinstance(spoofer_pulse_width_ns, list) else [spoofer_pulse_width_ns],
        noise_ratio if isinstance(noise_ratio, list) else [noise_ratio],
    ]

    param_list = cartesian(param_list_list)
    param_list = pl.DataFrame(param_list, schema=[
        ("pulse_num", pl.Int64),
        ("min_interval_ns", pl.Int64),
        ("max_interval_ns", pl.Int64),
        ("max_torelance_error_ns", pl.Int64),
        ("consider_amp", pl.Boolean),
        ("max_amp_diff_ratio", pl.Float64),
        ("max_amp_torelance_error", pl.Float64),
        ("outdoor_wall_distance_m", pl.Float64),
        ("outdoor_wall_reflectivity", pl.Float64),
        ("spoofer_frequency_mhz", pl.Float64),
        ("spoofer_pulse_width_ns", pl.Int64),
        ("noise_ratio", pl.Float64),
    ])

    return param_list

def get_cached_table() -> pl.DataFrame:
    try:
        return pl.read_csv("cache.csv")
    except:
        print("cache.csv not found")
    return pl.DataFrame([], schema=[
        ("pulse_num", pl.Int64),
        ("min_interval_ns", pl.Int64),
        ("max_interval_ns", pl.Int64),
        ("max_torelance_error_ns", pl.Int64),
        ("consider_amp", pl.Boolean),
        ("max_amp_diff_ratio", pl.Float64),
        ("max_amp_torelance_error", pl.Float64),
        ("outdoor_wall_distance_m", pl.Float64),
        ("outdoor_wall_reflectivity", pl.Float64),
        ("spoofer_frequency_mhz", pl.Float64),
        ("spoofer_pulse_width_ns", pl.Int64),
        ("noise_ratio", pl.Float64),
        ("ASR", pl.Float64),
        ("Lost Point Rate", pl.Float64),
    ])

def main():
    fastlyzer = Fastlyzer(
        f=calculation,
        cache_file_name="cache.csv",
        input_schema=[
            ("pulse_num", pl.Int64),
            ("min_interval_ns", pl.Int64),
            ("max_interval_ns", pl.Int64),
            ("max_torelance_error_ns", pl.Int64),
            ("consider_amp", pl.Boolean),
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
        "max_amp_diff_ratio": [0.4],
        "max_amp_torelance_error": [0.0, 0.02, 0.05, 0.08, 0.1],
        "outdoor_wall_distance_m": [50.0],
        "outdoor_wall_reflectivity": [0.8],
        "spoofer_frequency_mhz": np.arange(0.0, 30.1, 2.0).tolist(),
        "spoofer_pulse_width_ns": [5],
        "noise_ratio": np.arange(0.0, 0.11, 0.02).tolist(),
    })

    fastlyzer.visualize(
        x_col="spoofer_frequency_mhz",
        y_col="ASR",
        by_col="noise_ratio",
        const_cols={
            "min_interval_ns": 250,
            "max_interval_ns": 450,
            "max_torelance_error_ns": 20,
            "pulse_num": 2,
            "consider_amp": True,
            "max_amp_diff_ratio": 0.4,
            "max_amp_torelance_error": 0.05,
            "outdoor_wall_distance_m": 50.0,
            "outdoor_wall_reflectivity": 0.8,
            "spoofer_pulse_width_ns": 5,
        }
    )

    # target_params = generate_param_list(
    #     pulse_num=[1,2,3],
    #     min_interval_ns=250,
    #     max_interval_ns=450,
    #     max_torelance_error_ns=20,
    #     consider_amp=True,
    #     max_amp_diff_ratio=0.4,
    #     max_amp_torelance_error=0.05,
    #     outdoor_wall_distance_m=50.0,
    #     outdoor_wall_reflectivity=0.8,
    #     spoofer_frequency_mhz=np.arange(1.0, 10.1, 1.0).tolist(),
    #     spoofer_pulse_width_ns=5,
    #     noise_ratio=0.03
    # )

    # cached_table = get_cached_table()

    # merged_table = target_params.join(cached_table, on=[
    #     "pulse_num", "min_interval_ns", "max_interval_ns", "max_torelance_error_ns", "consider_amp", "max_amp_diff_ratio", "max_amp_torelance_error",
    #     "outdoor_wall_distance_m", "outdoor_wall_reflectivity", "spoofer_frequency_mhz", "spoofer_pulse_width_ns", "noise_ratio"
    # ], how="left")

    # no_cache_params = merged_table.filter(pl.col("ASR").is_null())
    # print("no_cache_params", no_cache_params.shape[0])
    # print("cached_params", merged_table.shape[0] - no_cache_params.shape[0])
    
    # use_multiprocessing = True
    # if use_multiprocessing:
    #     futures = []
    #     with ProcessPoolExecutor(max_workers=6) as executor:
    #         for param in no_cache_params.drop("ASR", "Lost Point Rate").to_dicts():
    #             futures.append(executor.submit(calculation, **param))

    #     asr_list = []
    #     lpr_list = []
    #     for future in futures:
    #         asr, lpr = future.result()
    #         asr_list.append(asr)
    #         lpr_list.append(lpr)
    # else:
    #     asr_list = []
    #     lpr_list = []
    #     for param in no_cache_params.drop("ASR", "Lost Point Rate").to_dicts():
    #         asr, lpr = calculation(**param)
    #         asr_list.append(asr)
    #         lpr_list.append(lpr)

    # np_cache_params = no_cache_params.with_columns([
    #     pl.Series("ASR", asr_list),
    #     pl.Series("Lost Point Rate", lpr_list)
    # ])

    # pl.concat([cached_table, np_cache_params]).write_csv("cache.csv")

    # x_col = "spoofer_frequency_mhz"
    # y_col = "ASR"
    # by_col = "pulse_num"
    # const_cols = {
    #     "min_interval_ns": 250,
    #     "max_interval_ns": 450,
    #     "max_torelance_error_ns": 20,
    #     "consider_amp": True,
    #     "max_amp_diff_ratio": 0.4,
    #     "max_amp_torelance_error": 0.05,
    #     "outdoor_wall_distance_m": 50.0,
    #     "outdoor_wall_reflectivity": 0.8,
    #     "spoofer_pulse_width_ns": 5,
    #     "noise_ratio": 0.03
    # }

    # table = pl.concat([cached_table, np_cache_params])
    # table = table.filter(*const_cols).select(pl.col("*").sort_by(x_col))

    # # pulse_numごとにx軸spoofer_frequency_mhz, y軸ASR, Lost Point Rateをプロット
    # fig, axs = plt.subplots(1, 1, figsize=(10, 10))
    # axs = axs if isinstance(axs, np.ndarray) else [axs]
    # for group_key, sub_table in table.group_by([by_col]):
    #     axs[0].plot(sub_table[x_col], sub_table[y_col], label=f"{by_col}={group_key}")
    # axs[0].set_title(f"{y_col} vs {x_col}")
    # axs[0].set_xlabel(x_col)
    # axs[0].set_ylabel(y_col)
    # axs[0].legend()
    # plt.show()

if __name__ == "__main__":
    main()