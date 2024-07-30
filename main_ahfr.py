from spaal2 import DummyLidarSony, DummyOutdoor, DummySpooferContinuousPulse, visualize, PreciseDuration, apply_noise, DummySpooferOff, DummyLidarVLP16, DummySpooferAdaptiveHFR
import time

import numpy as np
from plot_hist import PlotHist2

def main():

    lidar = DummyLidarVLP16()
    outdoor = DummyOutdoor(50.0, 0.8)
    spoofer = DummySpooferAdaptiveHFR(
        frequency=20 * 1e6, 
        duration=PreciseDuration(milliseconds=20),
        spoofer_distance_m=10.0,
        pulse_width=PreciseDuration(nanoseconds=5),
    )

    plotter = PlotHist2()

    start = time.time()
    point_list = []
    while True:
        try:
            config, signal = lidar.scan()

            if config.altitude == 900 and abs(config.azimuth - 1000) < 20:
                spoofer.trigger(config, signal)

            signal = apply_noise(outdoor.apply(signal), ratio=0.01)
            legitimate_signal = signal.copy()
            external_signal = apply_noise(spoofer.get_range_signal(config.start_timestamp, config.accept_duration), ratio=0.01)
            signal = np.choose(
                signal < external_signal,
                [signal, external_signal]
            )
            signal = np.clip(signal, 0, 9)
            points = lidar.receive(config, signal)
            point_list.extend(points)
        except StopIteration:
            break

    print(f"There are {len(point_list)}/{lidar.max_index} points in total. ({1 - len(point_list) / lidar.max_index:.2%} points are lost)")
    print(f"Time elapsed: {(time.time() - start)*1000:.2f}ms")
    visualize(point_list)
    # plotter.show()


if __name__ == "__main__":
    main()
