import numpy as np
import pandas as pd

from .configs import CommonConfig, LidarConfig
from .return_mode import ReturnMode


def calc_observed_points(
        received_wave: np.ndarray,
        cc: CommonConfig,
        lc: LidarConfig
):
    observed_points = []

    def add_observed_points(
            index: int, raise_list: np.ndarray, peak_list: np.ndarray, azimuth_radian: float):
        distance_m = raise_list[index] * cc.sampling_rate_ns * cc.c_ns / 2
        observed_points.append([
            azimuth_radian,
            distance_m,
            min(255.0, peak_list[index] * 255.0)
        ])

    for azimuth_index in range(lc.azimuth_size):
        first = azimuth_index * lc.azimuth_width_sample
        if lc.randomization_enabled:
            first += lc.randomization_per_azimuth_sample[azimuth_index]
        scan_first = max(0, first + lc.window_open_sample)
        scan_range = \
            received_wave[scan_first:first + lc.window_close_sample]
        raises = np.flatnonzero(
            (scan_range[:-1] < lc.trigger_height) & (scan_range[1:] > lc.trigger_height)
        ) + 1
        peaks = np.empty_like(raises, dtype=float)
        for i in range(len(raises)):
            peaks[i] = np.max(
                scan_range[raises[i]:min(len(scan_range), raises[i] + lc.peak_search_sample)]
            )
        # scan位置の分を補正
        if scan_first > 0:
            raises += lc.window_open_sample

        if lc.fingerprinting_enabled:
            raises_certified = []
            peaks_certified = []
            fp_pulse_num = lc.fingerprinting_pulse_offsets_sample.shape[1]
            error = lc.fingerprinting_acceptable_error_sample
            for i in range(len(raises) - fp_pulse_num + 1):
                certified = True
                for pulse_index in range(1, fp_pulse_num):
                    base_position = lc.fingerprinting_pulse_offsets_sample[azimuth_index,pulse_index]
                    exist = np.any((base_position - error <= raises - raises[i]) & (raises - raises[i] <= base_position + error))
                    if not exist:
                        certified = False
                        break
                if certified:
                    raises_certified.append(raises[i])
                    peaks_certified.append(peaks[i])

            raises = np.array(raises_certified)
            peaks = np.array(peaks_certified)

        azimuth_rad = azimuth_index / lc.azimuth_size * np.pi * 2
        if len(raises) > 0:
            if lc.return_mode is ReturnMode.FIRST:
                add_observed_points(0, raises, peaks, azimuth_rad)
            elif lc.return_mode is ReturnMode.STRONGEST:
                max_index = int(np.argmax(peaks))
                add_observed_points(max_index, raises, peaks, azimuth_rad)
            elif lc.return_mode is ReturnMode.LAST:
                add_observed_points(-1, raises, peaks, azimuth_rad)
            elif lc.return_mode is ReturnMode.DUAL:
                max_index = int(np.argmax(peaks))
                add_observed_points(max_index, raises, peaks, azimuth_rad)
                if len(peaks) >= 2:
                    if max_index == len(peaks):  # strongestとlastが一致する場合
                        second_strongest_index = np.argsort(peaks)[1]
                        add_observed_points(second_strongest_index, raises, peaks, azimuth_rad)
                    else:
                        add_observed_points(-1, raises, peaks, azimuth_rad)

    if len(observed_points) == 0:
        observed_points = np.zeros((0,3))
    else:
        observed_points = pd.DataFrame(observed_points).to_numpy()
    # 0.3m未満のものは除外
    observed_points = observed_points[observed_points[:, 1] >= 0.3, :]
    return observed_points
