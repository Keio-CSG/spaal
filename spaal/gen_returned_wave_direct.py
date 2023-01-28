import numpy as np

from .configs import LidarConfig, CommonConfig

def gen_firing_wave_direct(
    cc: CommonConfig,
    lc: LidarConfig,
) -> np.ndarray:
    wave = np.zeros((cc.ns2sample(lc.rotation_rate_ns),))

    for azimuth_index in range(lc.azimuth_size):
        delay_sample = cc.ns2sample(lc.delay_per_azimuth[azimuth_index])
        first = azimuth_index * lc.azimuth_width_sample + delay_sample
        if lc.randomization_enabled:
            first += lc.randomization_per_azimuth_sample[azimuth_index]
        if lc.fingerprinting_enabled:
            for i in range(lc.fingerprinting_pulse_offsets_sample.shape[1]):
                pulse_first = first + lc.fingerprinting_pulse_offsets_sample[azimuth_index,i]
                wave[pulse_first:pulse_first+cc.ns2sample(lc.pulse_width_ns)] = \
                    1.0 * lc.reflectance_per_azimuth[azimuth_index]
        else:
            wave[first:first+cc.ns2sample(lc.pulse_width_ns)] = \
                1.0 * lc.reflectance_per_azimuth[azimuth_index]
    return wave