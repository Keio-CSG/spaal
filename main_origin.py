from spaal2 import DummyLidarSony, DummyOutdoor, DummySpooferContinuousPulse, visualize, PreciseDuration, apply_noise, DummySpooferOff, gen_sunlight2
import time

import numpy as np
from plot_hist import PlotHist2

def main():

    # lidar = DummyLidarVLP16()
    lidar = DummyLidarSony(
        pulse_num=2,
        min_interval=PreciseDuration(nanoseconds=250),
        max_interval=PreciseDuration(nanoseconds=450),
        max_torelance_error=PreciseDuration(nanoseconds=20),
        consider_amp=True,
        min_amp_diff_ratio=0.2,
        max_amp_diff_ratio=0.4,
        max_amp_torelance_error=0.05,
        thd_factor=0.0,
    )
    outdoor = DummyOutdoor(50.0, 0.8)
    spoofer = DummySpooferContinuousPulse(frequency=30 * 1e6, pulse_width=PreciseDuration(nanoseconds=5))
    # spoofer = DummySpooferOff()

    plotter = PlotHist2()

    start = time.time()
    point_list = []
    while True:
        try:
            config, signal = lidar.scan()

            signal = apply_noise(outdoor.apply(signal), ratio=0.01)
            # signal = outdoor.apply(signal)
            legitimate_signal = signal.copy()
            # signal += apply_noise(spoofer.get_range_signal(config.start_timestamp, config.accept_duration), ratio=0.01)
            external_signal = apply_noise(spoofer.get_range_signal(config.start_timestamp, config.accept_duration), ratio=0.01)
            signal = np.choose(
                signal < external_signal,
                [signal, external_signal]
            )
            sunlight = gen_sunlight2(len(signal), mean=2.0)
            signal = np.choose(
                signal < sunlight,
                [signal, sunlight]
            )
            signal = np.clip(signal, 0, 9)
            points, echoes = lidar.receive(config, signal)
            point_list.extend(points)
            plotter.record(signal, legitimate_signal, echoes, 
                           f"{lidar.index}: {config.consider_amp} {config.amp_torelance_error_ratio} {config.gt_amps_ratio} {config.gt_intervals}")
        except StopIteration:
            break

    print(f"There are {len(point_list)}/{lidar.max_index} points in total. ({1 - len(point_list) / lidar.max_index:.2%} points are lost)")
    print(f"Time elapsed: {(time.time() - start)*1000:.2f}ms")
    # visualize(point_list)
    plotter.show()


if __name__ == "__main__":
    main()
