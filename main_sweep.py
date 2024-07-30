from spaal2 import DummyLidarSony, DummyOutdoor, DummySpooferContinuousPulse, visualize, PreciseDuration, apply_noise
import time
from concurrent.futures import ProcessPoolExecutor

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

def calculation(
        attack_frequency: float,
        pulse_num: int,
        consider_amp: bool,
        noise_ratio: float,
):
    print(f"attack_frequency: {attack_frequency / 1e6}MHz, pulse_num: {pulse_num}, consider_amp: {consider_amp}, noise_ratio: {noise_ratio}")
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

def sweep(
        frequencies: np.ndarray,
        pulse_num: int,
        consider_amp: bool,
        noise_ratio: float,):
    result_list = []
    with ProcessPoolExecutor() as executor:
        for frequency in frequencies:
            result_list.append(executor.submit(calculation, frequency, pulse_num, consider_amp, noise_ratio))
    
    asr_list = []
    lost_point_list = []
    for result in result_list:
        asr, lost_point = result.result()
        asr_list.append(asr)
        lost_point_list.append(lost_point)
    
    return asr_list, lost_point_list

def main():

    # lidar = DummyLidarVLP16()

    params = [
        (2, False, 0.03),
        (1, False, 0.03),
        (2, True, 0.03),
        (3, False, 0.03),
    ]

    result_list = []

    frequencies = np.arange(1.1, 30.1, 2.0)[::-1]

    for param in params:
        result_list.append(sweep(frequencies * 1e6, *param))

    
    for asr_list, lost_list in result_list:
        plt.plot(frequencies, asr_list)
        plt.plot(frequencies, lost_list)

    plt.legend([
        "2 pulse", "2 pulse(lost)",
        "1 pulse", "1 pulse(lost)",
        "2 pulse with amp", "2 pulse with amp(lost)",
        "3 pulse", "3 pulse(lost)"
    ])
    plt.xlabel("Attack Frequency [MHz]")
    plt.ylabel("Attack Success Rate / Lost Point Rate")
    plt.show()


    # frequencies = np.arange(1.0, 30.1, 1.0) * 1e6
    # asr_list = []
    # asr_list2 = []
    # asr_list3 = []
    # asr_list4 = []
    # for frequency in frequencies:
    #     lidar = DummyLidarSony(
    #         pulse_num=2,
    #         min_interval=PreciseDuration(nanoseconds=250),
    #         max_interval=PreciseDuration(nanoseconds=450),
    #         max_torelance_error=PreciseDuration(nanoseconds=10),
    #     )
    #     lidar2 = DummyLidarSony()
    #     lidar3 = DummyLidarSony(
    #         pulse_num=2,
    #         min_interval=PreciseDuration(nanoseconds=250),
    #         max_interval=PreciseDuration(nanoseconds=450),
    #         max_torelance_error=PreciseDuration(nanoseconds=10),
    #         consider_amp=True,
    #         max_amp_diff_ratio=0.5,
    #         max_amp_torelance_error=0.15,
    #     )
    #     lidar4 = DummyLidarSony(
    #         pulse_num=3,
    #         min_interval=PreciseDuration(nanoseconds=250),
    #         max_interval=PreciseDuration(nanoseconds=450),
    #         max_torelance_error=PreciseDuration(nanoseconds=10),
    #     )
    #     outdoor = DummyOutdoor(50.0, 0.6)
    #     spoofer = DummySpooferContinuousPulse(frequency=frequency, pulse_width=PreciseDuration(nanoseconds=5))

    #     point_list = []
    #     point_list2 = []
    #     point_list3 = []
    #     point_list4 = []
    #     while True:
    #         try:
    #             config, signal = lidar.scan()
    #             config2, signal2 = lidar2.scan()
    #             config3, signal3 = lidar3.scan()
    #             config4, signal4 = lidar4.scan()

    #             signal = apply_noise(outdoor.apply(signal))
    #             signal2 = apply_noise(outdoor.apply(signal2))
    #             signal3 = apply_noise(outdoor.apply(signal3))
    #             signal4 = apply_noise(outdoor.apply(signal4))
    #             attack_signal = apply_noise(spoofer.get_range_signal(config.start_timestamp, config.accept_duration))
    #             signal = np.clip(signal + attack_signal, 0, 9)
    #             signal2 = np.clip(signal2 + attack_signal, 0, 9)
    #             signal3 = np.clip(signal3 + attack_signal, 0, 9)
    #             signal4 = np.clip(signal4 + attack_signal, 0, 9)
    #             points, echoes = lidar.receive(config, signal)
    #             points2, echoes2 = lidar2.receive(config2, signal2)
    #             points3, echoes3 = lidar3.receive(config3, signal3)
    #             points4, echoes4 = lidar4.receive(config4, signal4)

    #             point_list.extend(points)
    #             point_list2.extend(points2)
    #             point_list3.extend(points3)
    #             point_list4.extend(points4)

    #         except StopIteration:
    #             break
    #     point_num = lidar.max_index
    #     remain_point_num = len([x for x in point_list if x.distance_m > 49.5 and x.distance_m < 50.5])
    #     print(f"{frequency/1e6}MHz... remain / all = {remain_point_num} / {point_num} = {remain_point_num / point_num * 100:.2f}%")
    #     asr_list.append(1 - remain_point_num / point_num)

    #     point_num = lidar2.max_index
    #     remain_point_num = len([x for x in point_list2 if x.distance_m > 49.5 and x.distance_m < 50.5])
    #     print(f"{frequency/1e6}MHz... remain / all = {remain_point_num} / {point_num} = {remain_point_num / point_num * 100:.2f}%")
    #     asr_list2.append(1 - remain_point_num / point_num)

    #     point_num = lidar3.max_index
    #     remain_point_num = len([x for x in point_list3 if x.distance_m > 49.5 and x.distance_m < 50.5])
    #     print(f"{frequency/1e6}MHz... remain / all = {remain_point_num} / {point_num} = {remain_point_num / point_num * 100:.2f}%")
    #     asr_list3.append(1 - remain_point_num / point_num)

    #     point_num = lidar4.max_index
    #     remain_point_num = len([x for x in point_list4 if x.distance_m > 49.5 and x.distance_m < 50.5])
    #     print(f"{frequency/1e6}MHz... remain / all = {remain_point_num} / {point_num} = {remain_point_num / point_num * 100:.2f}%")
    #     asr_list4.append(1 - remain_point_num / point_num)

    # df = pd.DataFrame(
    #     [
    #         asr_list,
    #         asr_list2,
    #         asr_list3,
    #         asr_list4
    #     ],
    #     index=["2 pulse", "1 pulse", "2 pulse with amp", "3 pulse"],
    #     columns=frequencies / 1e6,
    # )
    # df.to_csv("result.csv")

    # plt.plot(frequencies / 1e6, asr_list, label="2 pulse")
    # plt.plot(frequencies / 1e6, asr_list2, label="1 pulse")
    # plt.plot(frequencies / 1e6, asr_list3, label="2 pulse with amp")
    # plt.plot(frequencies / 1e6, asr_list4, label="3 pulse")
    # plt.legend()
    # plt.show()

    # visualize(point_list)


if __name__ == "__main__":
    main()
