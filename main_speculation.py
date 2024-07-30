from spaal2 import DummyLidarSony, DummyOutdoor, DummySpooferContinuousPulse, visualize, PreciseDuration, apply_noise, DummySpooferOff, DummyLidarVLP16, DummySpooferAdaptiveHFRWithSpeculation, DummySpooferAdaptiveHFR
import time
import random

import numpy as np
import matplotlib.pyplot as plt
from plot_hist import PlotHist2

def main():

    lidar = DummyLidarVLP16()
    outdoor = DummyOutdoor(50.0, 0.8)
    spoofer = DummySpooferAdaptiveHFRWithSpeculation(
        frequency=5 * 1e6, 
        duration=PreciseDuration(milliseconds=20),
        frame_interval=PreciseDuration(milliseconds=100),
        spoofer_distance_m=10.0,
        pulse_width=PreciseDuration(nanoseconds=5),
    )
    spoofer2 = DummySpooferAdaptiveHFR(
        frequency=5 * 1e6,
        duration=PreciseDuration(milliseconds=20),
        spoofer_distance_m=10.0,
        pulse_width=PreciseDuration(nanoseconds=5),
    )
    base_timestamp = PreciseDuration.zero();

    plotter = PlotHist2()

    asr_list1 = []
    asr_list2 = []

    start = time.time()
    for frame in range(20):
        point1_list = []
        point2_list = []
        while True:
            try:
                config, signal = lidar.scan()

                if config.altitude == 900 and abs(config.azimuth - 1000) < 20:
                    if random.random() < 0.5:
                        spoofer.trigger(config, signal)
                        spoofer2.trigger(config, signal)
                    else:
                        print(f"speculation")

                signal = apply_noise(outdoor.apply(signal), ratio=0.01)
                external_signal = apply_noise(spoofer.get_range_signal(config.start_timestamp, config.accept_duration), ratio=0.01)
                signal1 = np.choose(
                    signal < external_signal,
                    [signal, external_signal]
                )
                external_signal = apply_noise(spoofer2.get_range_signal(config.start_timestamp, config.accept_duration), ratio=0.01)
                signal2 = np.choose(
                    signal < external_signal,
                    [signal, external_signal]
                )
                signal1 = np.clip(signal1, 0, 9)
                signal2 = np.clip(signal2, 0, 9)
                points1 = lidar.receive(config, signal1)
                point1_list.extend(points1)
                points2 = lidar.receive(config, signal2)
                point2_list.extend(points2)
            except StopIteration:
                break

        base_timestamp += spoofer.frame_interval
        lidar = lidar.new_frame(base_timestamp)

        remain_point_num1 = len([x for x in point1_list if x.distance_m > 49.5 and x.distance_m < 50.5])
        asr = (1 - remain_point_num1 / lidar.max_index) * 100
        asr_list1.append(asr)
        remain_point_num2 = len([x for x in point2_list if x.distance_m > 49.5 and x.distance_m < 50.5])
        asr = (1 - remain_point_num2 / lidar.max_index) * 100
        asr_list2.append(asr)

        print(f"There are {len(point1_list)}/{lidar.max_index} points in total. ({1 - len(point1_list) / lidar.max_index:.2%} points are lost)")
        print(f"Time elapsed: {(time.time() - start)*1000:.2f}ms")
        # visualize(point_list)
    # plotter.show()
    plt.plot(asr_list1)
    plt.plot(asr_list2)
    plt.show()


if __name__ == "__main__":
    main()
