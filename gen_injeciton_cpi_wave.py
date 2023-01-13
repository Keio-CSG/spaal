import numpy as np

from .configs import CommonConfig, SpooferConfig, LidarConfig


def gen_injection_cpi_wave(
        firing_wave: np.ndarray,
        cc: CommonConfig,
        sc: SpooferConfig,
        delay_ns: float,
        interval_ns: float
) -> np.ndarray:
    """

    params:
    - enable_phase: 位相をランダムに変更するかどうか。Falseの場合0からスタートする
    """
    injection_wave = np.zeros_like(firing_wave)

    # 最初のパルス立ち上がりを検出
    first_pulse = np.where(firing_wave > 0)[0][0]
    delay_sample = cc.ns2sample(delay_ns)
    interval_sample = cc.ns2sample(interval_ns)
    current_position = first_pulse + delay_sample
    while current_position < len(injection_wave) - sc.injection_pulse_width_sample:
        injection_wave[current_position:current_position+sc.injection_pulse_width_sample] = \
            sc.pulse_strength
        current_position += interval_sample

    return injection_wave
