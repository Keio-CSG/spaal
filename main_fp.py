from spaal2 import DummyLidarSony, DummyOutdoor, DummySpooferContinuousPulse, visualize, PreciseDuration
import time

import matplotlib.pyplot as plt
import numpy as np

def main():

    # lidar = DummyLidarVLP16()
    lidar = DummyLidarSony(
        pulse_num=2,
        min_interval=PreciseDuration(nanoseconds=50),
        max_interval=PreciseDuration(nanoseconds=100),
        max_torelance_error=PreciseDuration(nanoseconds=10),
    )
    outdoor = DummyOutdoor(50.0, 0.6)
    spoofer = DummySpooferContinuousPulse(frequency=1 * 1e6, pulse_width=PreciseDuration(nanoseconds=10))

    start = time.time()
    point_list = []
    is_first = True
    while True:
        try:
            config, signal = lidar.scan()

            signal = outdoor.apply(signal)
            legitimate_signal = signal.copy()
            signal += spoofer.get_range_signal(config.start_timestamp, config.accept_duration)
            signal = np.clip(signal, 0, 9)
            points, echoes = lidar.receive(config, signal)
            if is_first:
                plt.bar(np.arange(len(signal)), signal, width=1.0)
                plt.bar(np.arange(len(legitimate_signal)), legitimate_signal, width=1.0, color='green')
                plt.scatter([x[0].peak_position for x in echoes], [x[0].peak_height for x in echoes], color='red')
                for i, x in enumerate(echoes):
                    plt.axvline(x=x[0].peak_position - x[0].width/2, color='green', linestyle='--')
                    plt.axvline(x=x[0].peak_position + x[0].width/2, color='green', linestyle='--')
                    plt.text(x[0].peak_position, x[0].peak_height, f'{i}', color='red', size=30)
                    if len(x) == 4:
                        for e in x:
                            plt.text(e.peak_position, e.peak_height, f'{i}', color='blue', size=10)
                plt.show()
            # is_first = False
            point_list.extend(points)
        except StopIteration:
            break

    print(f"There are {len(point_list)} points.")
    print(f"Time elapsed: {(time.time() - start)*1000:.2f}ms")
    visualize(point_list)


if __name__ == "__main__":
    main()
