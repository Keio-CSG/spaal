import numpy as np

from .configs import CommonConfig, LidarConfig


def gen_returned_wave(
        wave: np.ndarray,
        cc: CommonConfig,
        lc: LidarConfig
) -> np.ndarray:
    returned_wave = np.zeros_like(wave)
    for azimuth_index in range(lc.azimuth_size):
        delay_sample = cc.ns2sample(lc.delay_per_azimuth[azimuth_index])
        first = azimuth_index * lc.azimuth_width_sample
        if lc.randomization_enabled:
            first += lc.randomization_per_azimuth_sample[azimuth_index]
        wave_view = wave[first:first+lc.azimuth_width_sample-delay_sample]
        wave_mask = wave_view != 0
        returned_wave[first+delay_sample:first+lc.azimuth_width_sample][wave_mask] = \
            wave_view[wave_mask] * lc.reflectance_per_azimuth[azimuth_index]
        # returned_wave[first+delay_sample:first+lc.azimuth_width_sample] = \
        #     wave[first:first+lc.azimuth_width_sample-delay_sample] * \
        #     lc.reflectance_per_azimuth[azimuth_index]

    return returned_wave
