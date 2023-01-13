import numpy as np

from .configs import LidarConfig, CommonConfig


def gen_firing_wave(
        cc: CommonConfig,
        lc: LidarConfig
) -> np.ndarray:
    wave = np.zeros((cc.ns2sample(lc.rotation_rate_ns),))

    for azimuth_index in range(lc.azimuth_size):
        first = azimuth_index * lc.azimuth_width_sample
        if lc.randomization_enabled:
            first += lc.randomization_per_azimuth_sample[azimuth_index]
        if lc.fingerprinting_enabled:
            for i in range(lc.fingerprinting_pulse_offsets_sample.shape[1]):
                pulse_first = first + lc.fingerprinting_pulse_offsets_sample[azimuth_index,i]
                wave[pulse_first:pulse_first+cc.ns2sample(lc.pulse_width_ns)] = 1.0
        else:
            wave[first:first+cc.ns2sample(lc.pulse_width_ns)] = 1.0

    return wave
