from spaal2 import DummyLidarSony, DummyOutdoor, DummySpooferContinuousPulse, DummySpooferOff, PreciseDuration, apply_noise, gen_sunlight2

import numpy as np

def calculation(
        pulse_num: int,
        min_interval_ns: int,
        max_interval_ns: int,
        max_torelance_error_ns: int,
        consider_amp: bool,
        min_amp_diff_ratio: float,
        max_amp_diff_ratio: float,
        max_amp_torelance_error: float,
        outdoor_wall_distance_m: float,
        outdoor_wall_reflectivity: float,
        spoofer_frequency_mhz: float,
        spoofer_pulse_width_ns: int,
        noise_ratio: float,
        sunlight_level: float,
        thd_factor: float,
):
    print(f"spoofer_frequency_mhz: {spoofer_frequency_mhz}MHz, pulse_num: {pulse_num}, consider_amp: {consider_amp}, noise_ratio: {noise_ratio}")
    lidar = DummyLidarSony(
        pulse_num=pulse_num,
        min_interval=PreciseDuration(nanoseconds=min_interval_ns),
        max_interval=PreciseDuration(nanoseconds=max_interval_ns),
        max_torelance_error=PreciseDuration(nanoseconds=max_torelance_error_ns),
        consider_amp=consider_amp,
        min_amp_diff_ratio=min_amp_diff_ratio,
        max_amp_diff_ratio=max_amp_diff_ratio,
        max_amp_torelance_error=max_amp_torelance_error,
        thd_factor=thd_factor,
    )
    outdoor = DummyOutdoor(outdoor_wall_distance_m, outdoor_wall_reflectivity)
    if spoofer_frequency_mhz == 0:
        spoofer = DummySpooferOff()
    else:
        spoofer = DummySpooferContinuousPulse(
            frequency=spoofer_frequency_mhz*1e6, 
            pulse_width=PreciseDuration(nanoseconds=spoofer_pulse_width_ns))

    point_list = []
    while True:
        try:
            config, signal = lidar.scan()

            signal = apply_noise(outdoor.apply(signal), ratio=noise_ratio)
            # signal += apply_noise(spoofer.get_range_signal(config.start_timestamp, config.accept_duration), ratio=noise_ratio)
            external_signal = apply_noise(spoofer.get_range_signal(config.start_timestamp, config.accept_duration), ratio=noise_ratio)
            signal = np.choose(
                signal < external_signal,
                [signal, external_signal]
            )
            if sunlight_level > 0:
                sunlight = gen_sunlight2(len(signal), mean=sunlight_level)
                signal = np.choose(
                    signal < sunlight,
                    [signal, sunlight]
                )
            signal = np.clip(signal, 0, 9)
            points, echoes = lidar.receive(config, signal)
            point_list.extend(points)
        except StopIteration:
            break

    max_point_num = lidar.max_index
    available_point_num = len(point_list)
    min_accept_distance_m = outdoor_wall_distance_m - 0.5
    max_accept_distance_m = outdoor_wall_distance_m + 0.5
    remain_point_num = len([x for x in point_list if x.distance_m > min_accept_distance_m and x.distance_m < max_accept_distance_m])
    return {
        "ASR": 1 - remain_point_num / max_point_num, 
        "Lost Point Rate": 1 - available_point_num / max_point_num
    }
