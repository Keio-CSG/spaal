import numpy as np

from .configs import CommonConfig, SpooferConfig


def gen_injection_wave(
        returned_wave: np.ndarray,
        cc: CommonConfig,
        sc: SpooferConfig,
        enable_phase: bool = True
) -> np.ndarray:
    """

    params:
    - enable_phase: 位相をランダムに変更するかどうか。Falseの場合0からスタートする
    """
    hfr_interval_sample = cc.ns2sample(1 / sc.hfr_frequency_mhz * 1000)

    injection_wave = np.zeros_like(returned_wave)
    for i in range(int(len(injection_wave)/hfr_interval_sample)):
        first = i * hfr_interval_sample
        injection_wave[first:first+sc.injection_pulse_width_sample] = sc.pulse_strength

    if enable_phase:
        phase = np.random.rand()
        injection_wave = np.roll(injection_wave, int(hfr_interval_sample*phase))

    return injection_wave
