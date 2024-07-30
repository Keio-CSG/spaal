from spaal2 import DummyLidarSony, DummyOutdoor, DummySpooferContinuousPulse, visualize, PreciseDuration, apply_noise, DummySpooferOff
import time
from concurrent.futures import ProcessPoolExecutor

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def calculation(
        diff_ratio: float,
        torelance_error: float,
        noise_ratio: float,
):
    attack_frequency = 0
    pulse_num = 2
    consider_amp = True
    print(f"attack_frequency: {attack_frequency / 1e6}MHz, pulse_num: {pulse_num}, consider_amp: {consider_amp}, noise_ratio: {noise_ratio}")
    lidar = DummyLidarSony(
        pulse_num=pulse_num,
        min_interval=PreciseDuration(nanoseconds=250),
        max_interval=PreciseDuration(nanoseconds=450),
        max_torelance_error=PreciseDuration(nanoseconds=20),
        consider_amp=consider_amp,
        max_amp_diff_ratio=diff_ratio,
        max_amp_torelance_error=torelance_error,
    )
    outdoor = DummyOutdoor(50.0, 0.8)
    if attack_frequency == 0:
        spoofer = DummySpooferOff()
    else:
        spoofer = DummySpooferContinuousPulse(frequency=attack_frequency, pulse_width=PreciseDuration(nanoseconds=5))

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
    # (attack success rate, lost point rate)
    return (1 - remain_point_num / max_point_num), (1 - available_point_num / max_point_num)


def main():
    noise_list = np.linspace(0, 0.1, 11)
    diff_ratio_list = np.linspace(0, 0.5, 6)
    torelance_error_list = np.linspace(0, 0.1, 6)

    df = pd.DataFrame(columns=["diff_ratio", "torelance_error", "noise_ratio", "ASR", "Lost Point Rate"])
    for diff_ratio in diff_ratio_list:
        for torelance_error in torelance_error_list:
                for noise in noise_list:
                    asr, lost_point = calculation(diff_ratio, torelance_error, noise)
                    df.loc[f"{diff_ratio}_{torelance_error}_{noise}"] = [diff_ratio, torelance_error, noise, asr, lost_point]

    df.to_csv("result.csv")

    

if __name__ == "__main__":
    main()
