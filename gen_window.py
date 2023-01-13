import numpy as np

from .configs import LidarConfig


def gen_window_gaussian(
        lc: LidarConfig,
        center_degree: float,
        std_degree: float
) -> np.ndarray:
    window = np.full((lc.azimuth_size,), lc.degree_per_azimuth)
    window[0] = 0
    window = np.cumsum(window)
    window = np.exp( - (window - center_degree)**2 / (2*std_degree**2) )
    return window

def gen_window_band_pass(
        lc: LidarConfig,
        min_degree: float,
        max_degree: float
) -> np.ndarray:
    window = np.zeros((lc.azimuth_size,))
    min_index = int(min_degree / lc.degree_per_azimuth)
    max_index = int(max_degree / lc.degree_per_azimuth)
    window[min_index:max_index+1] = 1.0
    return window