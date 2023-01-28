from .return_mode import ReturnMode

import numpy as np

class CommonConfig:
    """
    共通のパラメータたち
    """
    def __init__(self,
                sampling_rate_ns: float,
                c_ns: float):
        """

        :param sampling_rate_ns: 波形1サンプルあたりの時間
        :param c_ns: 光速(m/ns)
        """
        self.sampling_rate_ns = sampling_rate_ns
        self.c_ns = c_ns

    def ns2sample(self, value_ns) -> int:
        return int(value_ns / self.sampling_rate_ns)

class LidarConfig:
    """
    LiDARのパラメータたち
    """
    def __init__(self,
                 cc: CommonConfig,
                 azimuth_interval_ns: float,
                 pulse_width_ns: float,
                 rotation_rate_ns: float,
                 wall_distance_m: float,
                 reflectance: float,
                 return_mode: ReturnMode,
                 receiving_window_open_ns: int,
                 receiving_window_close_ns: int,
                 peak_search_ns: int,
                 trigger_height: float,
                 randomization_max_ns: float = 0,
                 randomization_enabled: bool = False,
                 fingerprinting_min_interval_ns: float = 0,
                 fingerprinting_max_interval_ns: float = 0,
                 fingerprinting_pulse_num: int = 0,
                 fingerprinting_acceptable_error_ns: float = 0,
                 fingerprinting_enabled: bool = False):
        """

        :param cc: 共通コンフィグ
        :param azimuth_interval_ns: 1方位角あたりの周期時間
        :param pulse_width_ns: 射出するパルス幅
        :param rotation_rate_ns: LiDARが1周するのにかかる時間
        :param wall_distance_m: 反射する壁までの距離
        :param reflectance: 壁の反射率
        :param return_mode: パルス検出の方式
        :param receiving_window_open_ns: 受光窓が開くタイミング
        :param receiving_window_close_ns: 受光窓が閉じるタイミング
        :param peak_search_ns: 立ち上がりからピークを探索する時間幅
        :param trigger_height: 立ち上がり検出の閾値
        :param randomization_max_ns: ランダムの最大ズレ時間
        :param randomization_enabled: ランダムが有効かどうか
        :param fingerprinting_min_interval_ns: パルス間隔の最小時間
        :param fingerprinting_max_interval_ns: パルス間隔の最大時間
        :param fingerprinting_pulse_num: 1つあたりのパルス数
        :param fingerprinting_acceptable_error_ns: 許容されるパルス間隔のズレ
        :param fingerprinting_enabled: フィンガープリントが有効かどうか
        """
        self.cc = cc
        self.azimuth_interval_ns = azimuth_interval_ns
        self.pulse_width_ns = pulse_width_ns
        self.rotation_rate_ns = rotation_rate_ns
        self.return_mode = return_mode
        self.receiving_window_open_ns = receiving_window_open_ns
        self.receiving_window_close_ns = receiving_window_close_ns
        self.peak_search_ns = peak_search_ns
        self.trigger_height = trigger_height

        self.azimuth_size = int(rotation_rate_ns/azimuth_interval_ns)
        self.azimuth_width_sample = self.cc.ns2sample(azimuth_interval_ns)
        self.delay_per_azimuth = np.full((self.azimuth_size,), wall_distance_m*2/self.cc.c_ns)
        self.reflectance_per_azimuth = np.full((self.azimuth_size,), reflectance)
        self.degree_per_azimuth = azimuth_interval_ns/rotation_rate_ns * 360.0

        self.peak_search_sample = self.cc.ns2sample(peak_search_ns)
        self.window_open_sample = self.cc.ns2sample(receiving_window_open_ns)
        self.window_close_sample = self.cc.ns2sample(receiving_window_close_ns)

        self.randomization_enabled = randomization_enabled
        if self.randomization_enabled:
            self.randomization_per_azimuth_sample = \
                (np.random.random((self.azimuth_size,)) *
                 randomization_max_ns / self.cc.sampling_rate_ns).astype(int)

        self.fingerprinting_enabled = fingerprinting_enabled
        if self.fingerprinting_enabled:
            self.fingerprinting_acceptable_error_sample = cc.ns2sample(fingerprinting_acceptable_error_ns)
            max_interval_sample = cc.ns2sample(fingerprinting_max_interval_ns)
            min_interval_sample = cc.ns2sample(fingerprinting_min_interval_ns)
            self.fingerprinting_pulse_offsets_sample = \
                np.random.random((self.azimuth_size, fingerprinting_pulse_num)) * \
                (max_interval_sample - min_interval_sample) + min_interval_sample
            self.fingerprinting_pulse_offsets_sample[:,0] = 0
            self.fingerprinting_pulse_offsets_sample = \
                np.cumsum(self.fingerprinting_pulse_offsets_sample, axis=1).astype(int)



class SpooferConfig:
    """
    Spooferのパラメータたち
    """
    def __init__(self,
                 cc: CommonConfig,
                 hfr_frequency_mhz: float,
                 injection_pulse_width_ns: float,
                 pulse_strength: float = 1.0):
        """

        :param cc: 共通コンフィグ
        :param hfr_frequency_mhz: パルス周波数
        :param injection_pulse_width_ns: パルス幅
        """
        self.cc = cc
        self.hfr_frequency_mhz = hfr_frequency_mhz
        self.injection_pulse_width_ns = injection_pulse_width_ns
        self.pulse_strength = pulse_strength

        self.injection_pulse_width_sample = self.cc.ns2sample(injection_pulse_width_ns)
