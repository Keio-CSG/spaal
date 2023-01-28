from typing import Optional
import numpy as np

from .configs import CommonConfig, LidarConfig


def combine_waves(
        returned_wave: np.ndarray,
        injection_wave: np.ndarray,
        lc: LidarConfig,
        window: Optional[np.ndarray] = None,
        overwrite: bool = False
) -> np.ndarray:
    """

    params:
    - window: 窓関数。shape=(azimuth_size,)
    - overwrite: returned_waveとinjection_waveを上書きするかどうか
    """
    if window is None:
        if overwrite:
            returned_wave += injection_wave
            return returned_wave
        return returned_wave + injection_wave
    filtered_injection_wave = injection_wave.view() if overwrite else injection_wave.copy()
    for azimuth_index in range(lc.azimuth_size):
        first = azimuth_index * lc.azimuth_width_sample
        if lc.randomization_enabled:
            first += lc.randomization_per_azimuth_sample[azimuth_index]
        filtered_injection_wave[first:first+lc.azimuth_width_sample] *= window[azimuth_index]
    if overwrite:
        returned_wave += filtered_injection_wave
        return returned_wave
    return returned_wave + filtered_injection_wave
