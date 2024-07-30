from spaal2 import DummyLidarSony, DummyOutdoor, DummySpooferContinuousPulse, visualize, PreciseDuration
import time

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def calculation(frequency: float, pulse_num: int) -> float:
    lidar = DummyLidarSony(
        pulse_num=pulse_num,
        min_interval=PreciseDuration(nanoseconds=50),
        max_interval=PreciseDuration(nanoseconds=100),
        max_torelance_error=PreciseDuration(nanoseconds=10),
    )
    outdoor = DummyOutdoor(50.0, 0.6)
    spoofer = DummySpooferContinuousPulse(frequency=frequency, pulse_width=PreciseDuration(nanoseconds=10))

    point_list = []
    while True:
        try:
            config, signal = lidar.scan()

            signal = outdoor.apply(signal)
            signal += spoofer.get_range_signal(config.start_timestamp, config.accept_duration)
            signal = np.clip(signal, 0, 9)
            points, echoes = lidar.receive(config, signal)
            point_list.extend(points)
        except StopIteration:
            break
    
    max_point_num = lidar.max_index
    remain_point_num = len([x for x in point_list if x.distance_m > 49.5 and x.distance_m < 50.5])
    return (1 - remain_point_num / max_point_num) * 100  # attack success rate

def main():

    # lidar = DummyLidarVLP16()

    result_list = []
    spend_time_list = []
    frequencies = np.arange(1.0, 30.1, 1.0) * 1e6
    pulse_num_list = [3, 2, 1]
    for pulse_num in pulse_num_list:
        print(f"\r{pulse_num=}", end="")
        result_list.append([])
        spend_time_list.append([])
        for frequency in frequencies:
            print(f"\r{frequency=}", end="")
            start = time.time()
            result = calculation(frequency, pulse_num)
            spend_time = time.time() - start
            result_list[-1].append(result)
            spend_time_list[-1].append(spend_time)

    df = pd.DataFrame(result_list, index=pulse_num_list, columns=frequencies / 1e6)
    print(df)
    df.to_csv("result.csv")
    spend_time_df = pd.DataFrame(spend_time_list, index=pulse_num_list, columns=frequencies / 1e6)
    print(spend_time_df)
    spend_time_df.to_csv("spend_time.csv")

    plt.plot(frequencies / 1e6, result_list[0], label="3 pulses")
    plt.plot(frequencies / 1e6, result_list[1], label="2 pulses")
    plt.plot(frequencies / 1e6, result_list[2], label="1 pulse")
    plt.legend()
    plt.xlabel("Frequency [MHz]")
    plt.ylabel("Attack success rate [%]")
    plt.show()

if __name__ == "__main__":
    main()
