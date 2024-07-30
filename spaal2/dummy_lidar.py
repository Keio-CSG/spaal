import numpy as np
import numpy.typing as npt
import matplotlib.pyplot as plt
from scipy.signal import find_peaks
from typing import Tuple
import time

from .precise_duration import PreciseDuration
from .velo_point import VeloPoint
from .measurement_config import MeasurementConfig


class DummyLidarVLP16:
    vertical_angles: list[int] = [-15, 1, -13, 3, -11, 5, -9, 7, -7, 9, -5, 11, -3, 13, -1, 15]

    def __init__(self, base_timestamp: PreciseDuration = PreciseDuration(nanoseconds=0)) -> None:
        self.index: int = 0
        self.max_index: int = int(360 // 0.2 * 16)
        self.accept_window = PreciseDuration(nanoseconds=800)
        self.base_timestamp = base_timestamp
        print(f"LiDAR: VLP16")

    def new_frame(self, base_timestamp: PreciseDuration) -> "DummyLidarVLP16":
        """
        新しいフレームを作成する
        """
        return DummyLidarVLP16(base_timestamp=base_timestamp)

    def _get_current_angle(self) -> tuple[int, int]:
        """
        Returns the current azimuth and altitude.
        """
        horizontal_index = self.index // 16
        vertical_index = self.index % 16
        return horizontal_index * 20, self._vertical_index_to_altitude(vertical_index)

    def _vertical_index_to_altitude(self, index: int) -> int:
        """
        Returns the altitude for the given vertical index.
        """
        return self.vertical_angles[index] * 100

    def _get_current_timestamp(self) -> int:
        """
        Returns the current timestamp.
        """
        horizontal_index = self.index // 16
        vertical_index = self.index % 16
        return horizontal_index * 55296 + vertical_index * 2304 + self.base_timestamp.in_nanoseconds

    def scan(self) -> tuple[MeasurementConfig, npt.NDArray[np.float64]]:
        if self.index >= self.max_index:
            raise StopIteration()
        azimuth, altitude = self._get_current_angle()
        timestamp = self._get_current_timestamp()

        signal = np.zeros((self.accept_window.in_nanoseconds, ))
        signal[:10] = 1.0

        self.index += 1
        return MeasurementConfig(
            start_timestamp=PreciseDuration(nanoseconds=timestamp),
            accept_duration=self.accept_window,
            azimuth=azimuth,
            altitude=altitude,
        ), signal

    def receive(self, config: MeasurementConfig, signal: npt.NDArray[np.float64]) -> list[VeloPoint]:
        raises = np.flatnonzero(
            (signal[:-1] < 0.01) & (signal[1:] >= 0.01)
        ) + 1
        peaks = np.empty_like(raises, dtype=object)
        for i in range(len(raises)):
            peaks[i] = np.max(
                signal[raises[i]:min(len(signal), raises[i] + 10)]
            )

        # get the highest peak
        highest_peak_index = np.argmax(peaks)
        highest_peak = peaks[highest_peak_index]
        highest_peak_time = raises[highest_peak_index]

        intensity = int(min(highest_peak * 255, 255))
        distance_m = highest_peak_time * 0.15
        alpha = np.deg2rad(config.azimuth / 100.0)
        omega = np.deg2rad(config.altitude / 100.0)
        x = distance_m * np.sin(alpha) * np.cos(omega)
        y = distance_m * np.cos(alpha) * np.cos(omega)
        z = distance_m * np.sin(omega)

        return [
            VeloPoint(
                intensity=intensity,
                channel=0,
                timestamp=config.start_timestamp.in_nanoseconds,
                azimuth=config.azimuth,
                altitude=config.altitude,
                distance_m=distance_m,
                x=x,
                y=y,
                z=z,
            )
        ]


class FireAngle:
    def __init__(self, v_angle: float, h_offset: float) -> None:
        self.v_angle = v_angle
        self.h_offset = h_offset


class DummyLidarVLP32c:
    fire_angles: list[FireAngle] = [
        FireAngle(-25, 1.4), FireAngle(-1, -4.2),
        FireAngle(-1.667, 1.4), FireAngle(-15.639, -1.4),
        FireAngle(-11.31, 1.4), FireAngle(0, -1.4),
        FireAngle(-0.667, 4.2), FireAngle(-8.843, -1.4),
        FireAngle(-7.254, 1.4), FireAngle(0.333, -4.2),
        FireAngle(-0.333, 1.4), FireAngle(-6.148, -1.4),
        FireAngle(-5.333, 4.2), FireAngle(1.333, -1.4),
        FireAngle(0.667, 4.2), FireAngle(-4, -1.4),
        FireAngle(-4.667, 1.4), FireAngle(1.667, -4.2),
        FireAngle(1, 1.4), FireAngle(-3.667, -4.2),
        FireAngle(-3.333, 4.2), FireAngle(3.333, -1.4),
        FireAngle(2.333, 1.4), FireAngle(-2.667, -1.4),
        FireAngle(-3, 1.4), FireAngle(7, -1.4),
        FireAngle(4.667, 1.4), FireAngle(-2.333, -4.2),
        FireAngle(-2, 4.2), FireAngle(15, -1.4),
        FireAngle(10.333, 1.4), FireAngle(-1.333, -1.4)]

    def __init__(self) -> None:
        self.index: int = 0
        self.max_index: int = int(360 // 0.2 * 32)
        self.accept_window = PreciseDuration(nanoseconds=800)
        print(f"LiDAR: VLP32c")

    def _get_current_angle(self) -> tuple[int, int]:
        """
        Returns the current azimuth and altitude.
        """
        horizontal_index = self.index // 32
        vertical_index = self.index % 32
        fire_angle = self.fire_angles[vertical_index]
        azimuth = int(horizontal_index * 20 + fire_angle.h_offset * 100)
        altitude = int(fire_angle.v_angle * 100)
        return azimuth, altitude

    def _get_current_timestamp(self) -> int:
        """
        Returns the current timestamp.
        """
        horizontal_index = self.index // 32
        vertical_index = int((self.index % 32) // 2)
        return horizontal_index * 55296 + vertical_index * 2304

    def scan(self) -> tuple[MeasurementConfig, npt.NDArray[np.float64]]:
        if self.index >= self.max_index:
            raise StopIteration()
        azimuth, altitude = self._get_current_angle()
        timestamp = self._get_current_timestamp()

        signal = np.zeros((self.accept_window.in_nanoseconds, ))
        signal[:10] = 1.0

        self.index += 1
        return MeasurementConfig(
            start_timestamp=PreciseDuration(nanoseconds=timestamp),
            accept_duration=self.accept_window,
            azimuth=azimuth,
            altitude=altitude,
        ), signal

    def receive(self, config: MeasurementConfig, signal: npt.NDArray[np.float64]) -> list[VeloPoint]:
        raises = np.flatnonzero(
            (signal[:-1] < 0.5) & (signal[1:] >= 0.5)
        ) + 1
        peaks = np.empty_like(raises, dtype=object)
        for i in range(len(raises)):
            peaks[i] = np.max(
                signal[raises[i]:min(len(signal), raises[i] + 10)]
            )
        if peaks.size == 0:
            return []

        # get the highest peak
        highest_peak_index = np.argmax(peaks)
        highest_peak = peaks[highest_peak_index]
        highest_peak_time = raises[highest_peak_index]

        intensity = int(min(highest_peak * 255, 255))
        distance_m = highest_peak_time * 0.15
        alpha = np.deg2rad(config.azimuth / 100.0)
        omega = np.deg2rad(config.altitude / 100.0)
        x = distance_m * np.sin(alpha) * np.cos(omega)
        y = distance_m * np.cos(alpha) * np.cos(omega)
        z = distance_m * np.sin(omega)

        return [
            VeloPoint(
                intensity=intensity,
                channel=0,
                timestamp=config.start_timestamp.in_nanoseconds,
                azimuth=config.azimuth,
                altitude=config.altitude,
                distance_m=distance_m,
                x=x,
                y=y,
                z=z,
            )
        ]

class Echo:
    """
    エコーを表すクラス
    """
    """
    self.peak_position: int
        エコーのピークの位置(index)
    self.peak_height: float
        エコーのピークの高さ
    self.width: int
        エコーの幅(index)
    """
    def __init__(self, peak_position: int, peak_height: float, width: int) -> None:
        self.peak_position = peak_position
        self.peak_height = peak_height
        self.width = width

class EchoGroup:
    """
    複数回発射などの場合用に、エコーの集合を表現するクラス
    """
    """
    self.echoes: list[Echo]
        エコーのリスト。出現順に整列
    """
    def __init__(self, echoes: list[Echo]) -> None:
        self.echoes = echoes

    def __getitem__(self, index: int) -> Echo:
        return self.echoes[index]
    
    def __len__(self) -> int:
        return len(self.echoes)

class DummyLidarSony:
    """
    SONY LiDAR SRLを模擬したLiDAR
    """
    """
    self.index: int
        現在の測距位置(0 ~ 192*56)
    self.max_index: int
        測距点数
    self.accept_window: PreciseDuration
        受光窓のサイズ
    self.pulse_half_width: PreciseDuration
        射出するパルスの幅
    self.peak_offset: int
        射出するパルスの時間遅れ。0nsで射出するパルスの形状が崩れないようにするために設定
    self.min_distance: int
        最小の測距距離(m)
    self.pulse_num: int
        1回の測距で射出するパルスの数。1回ならFingerprintなし。最大4
    self.min_interval: PreciseDuration
        複数パルスを射出する場合の最小のパルス間隔
    self.max_interval: PreciseDuration
        複数パルスを射出する場合の最大のパルス間隔
    self.max_torelance_error: PreciseDuration
        受光時に許容するパルス間隔のズレ
    self.consider_amp: bool
        Fingerprintに振幅変調を利用するかどうか。pulse_num==1の場合は無効
    self.min_amp_diff_ratio: float
        振幅変調の最小振幅比
    self.max_amp_diff_ratio: float
        振幅変調の最大振幅比
    self.max_amp_torelance_error: float
        振幅変調の許容誤差比
    self.debug: bool
        デバッグログを出力するかどうか
    """
    def __init__(self,
                 max_distance: float = 150.0,
                 pulse_num: int = 1, 
                 min_interval: PreciseDuration = PreciseDuration(nanoseconds=250), 
                 max_interval: PreciseDuration = PreciseDuration(nanoseconds=450),
                 max_torelance_error: PreciseDuration = PreciseDuration(nanoseconds=10),
                 consider_amp: bool = False,
                 min_amp_diff_ratio: float = 0.0,
                 max_amp_diff_ratio: float = 0.4,
                 max_amp_torelance_error: float = 0.2,
                 base_timestamp: PreciseDuration = PreciseDuration(nanoseconds=0),
                 thd_factor: float = 1.0,
                 debug: bool = False) -> None:
        self.index: int = 0
        self.max_index: int = 192 * 56
        self.max_distance = max_distance
        neccecary_time = max_distance / 0.15 + (pulse_num-1) * max_interval.in_nanoseconds
        self.accept_window = PreciseDuration(nanoseconds=int(neccecary_time))
        self.pulse_half_width = PreciseDuration(nanoseconds=5)
        self.peak_offset = 10
        self.min_distance = 0
        self.pulse_num = pulse_num
        self.min_interval = min_interval
        self.max_interval = max_interval
        self.max_torelance_error = max_torelance_error
        self.consider_amp = consider_amp if pulse_num >= 2 else False
        self.min_amp_diff_ratio = min_amp_diff_ratio
        self.max_amp_diff_ratio = max_amp_diff_ratio
        self.max_amp_torelance_error = max_amp_torelance_error
        self.base_timestamp = base_timestamp
        self.thd_factor = thd_factor
        if debug:
            print(f"LiDAR: SONY SRL")
            print(f"\tPulse Num: {self.pulse_num}")
            print(f"\tMin Interval: {self.min_interval}")
            print(f"\tMax Interval: {self.max_interval}")
            print(f"\tMax Torelance Error: {self.max_torelance_error}")
            print(f"\tConsider Amp: {self.consider_amp}")
            print(f"\tMin Amp Diff Ratio: {self.min_amp_diff_ratio}")
            print(f"\tMax Amp Diff Ratio: {self.max_amp_diff_ratio}")
            print(f"\tMax Amp Torelance Error: {self.max_amp_torelance_error}")

        # パルス形状を事前計算
        sigma = self.pulse_half_width.in_nanoseconds / (2 * np.sqrt(2 * np.log2(2)))
        pulse_x = np.arange(-3 * sigma, 3 * sigma, 1.0)
        self.pulse_shape = 9 * np.exp(-((pulse_x) ** 2) / (2 * sigma ** 2))
        self.one_scan_base = np.zeros((self.accept_window.in_nanoseconds, ))
        start = max(0, self.peak_offset - self.pulse_shape.size // 2)
        end = start + self.pulse_shape.size
        self.one_scan_base[start:end] = self.pulse_shape

        self.rng = np.random.default_rng()

        # パフォーマンス測定用の変数
        self.peak_det_time_accum = 0
        self.echo_pick_time_accum = 0
        self.echo_analysis_time_accum = 0
        self.fingerprint_time_accum = 0
        self.sort_time_accum = 0
        self.calc_pcd_time_accum = 0

    def new_frame(self, base_timestamp: PreciseDuration) -> "DummyLidarSony":
        """
        新しいフレームを作成する
        """
        return DummyLidarSony(
            max_distance=self.max_distance,
            pulse_num=self.pulse_num,
            min_interval=self.min_interval,
            max_interval=self.max_interval,
            max_torelance_error=self.max_torelance_error,
            consider_amp=self.consider_amp,
            min_amp_diff_ratio=self.min_amp_diff_ratio,
            max_amp_diff_ratio=self.max_amp_diff_ratio,
            max_amp_torelance_error=self.max_amp_torelance_error,
            base_timestamp=base_timestamp,
        )

    def _get_current_angle(self) -> tuple[int, int]:
        """
        現在のindexから測距方向を算出する

        Returns:
            tuple[int, int]: 
                測距方向(azimuth, altitude)
        """
        horizontal_index = self.index % 192
        vertical_index = self.index // 192
        return horizontal_index * 47 - 4512, vertical_index * 47 - 1316

    def _get_current_timestamp(self) -> int:
        """
        現在のindexから測距開始時間を算出する

        Returns:
            int: 
                測距開始時間(ns)
        """
        # 本来SRLは96点を同時に測距するが、変化が欲しいので1点ずつ測距する方式に変更
        # slot = self.index // 96
        slot = self.index
        return slot * 1748 * 1000 + self.base_timestamp.in_nanoseconds

    def scan(self) -> tuple[MeasurementConfig, npt.NDArray[np.float64]]:
        """
        現在のindexについて測距のために射出した信号と、その設定を算出
        """
        if self.index >= self.max_index:
            # indexが最大値に達していたら終了シグナルを出す
            raise StopIteration()
        azimuth, altitude = self._get_current_angle()
        timestamp = self._get_current_timestamp()

        # 射出信号を計算する
        if self.pulse_num == 1:
            # Fingerprintなしの場合
            signal = self.one_scan_base.copy()
            gt_intervals = []
        elif self.consider_amp:
            # Fingerprintあり & 振幅変調あり

            # それぞれのパルス位置を計算
            # 例えば、pulse_num=3, min_interval=100, max_interval=200の場合
            # [120, 170] -> [120, 290]
            gt_intervals = np.random.randint(
                self.min_interval.in_nanoseconds, 
                self.max_interval.in_nanoseconds, 
                self.pulse_num - 1
            ).cumsum().tolist()

            # それぞれのパルスの振幅比を計算
            # いずれかのパルスが振幅1.0で、その他のパルスは1-min_diff_ratioと1-max_diff_ratioの間でランダムに決定される
            # 例えば、pulse_num=3, min_diff_ratio=0.2, max_diff_ratio=0.4の場合
            # [1.0, 0.65, 0.8] -> [0.65, 1.0, 0.8]
            gt_amps = self.rng.permutation(
                np.hstack([
                    1.0, 
                    self.rng.random(self.pulse_num-1) * (self.max_amp_diff_ratio - self.min_amp_diff_ratio) + (1 - self.max_amp_diff_ratio)
                ])
            )

            # gt_intervalsとgt_ampsから信号を計算
            signal = self.one_scan_base.copy() * gt_amps[0]
            for i in range(self.pulse_num-1):
                mean = self.peak_offset + gt_intervals[i]

                start = mean - self.pulse_shape.size // 2
                end = start + self.pulse_shape.size
                signal[start:end] = self.pulse_shape * gt_amps[i+1]
        else:
            # Fingerprintあり & 振幅変調なし

            # それぞれのパルスの振幅比を計算
            # いずれかのパルスが振幅1.0で、その他のパルスは1-min_diff_ratioと1-max_diff_ratioの間でランダムに決定される
            # 例えば、pulse_num=3, min_diff_ratio=0.2, max_diff_ratio=0.4の場合
            # [1.0, 0.65, 0.8] -> [0.65, 1.0, 0.8]
            gt_intervals = np.random.randint(
                self.min_interval.in_nanoseconds, 
                self.max_interval.in_nanoseconds, 
                self.pulse_num - 1
            ).cumsum().tolist()

            # gt_intervalsから信号を計算
            signal = self.one_scan_base.copy()
            for i in range(self.pulse_num-1):
                mean = self.peak_offset + gt_intervals[i]

                start = mean - self.pulse_shape.size // 2
                end = start + self.pulse_shape.size
                signal[start:end] = self.pulse_shape

        self.index += 1
        return MeasurementConfig(
            start_timestamp=PreciseDuration(nanoseconds=timestamp),
            accept_duration=self.accept_window,
            azimuth=azimuth,
            altitude=altitude,
            torelance_error=self.max_torelance_error,
            gt_intervals=gt_intervals,
            consider_amp=self.consider_amp,
            gt_amps_ratio=gt_amps.tolist() if self.consider_amp else [],
            amp_torelance_error_ratio=self.max_amp_torelance_error,
        ), signal

    def receive(self, config: MeasurementConfig, signal: npt.NDArray[np.float64]) -> Tuple[list[VeloPoint], list[EchoGroup]]:
        """
        受光した信号からと測距情報から点群を計算
        """
        effective_echoes = detect_echo(signal, self.thd_factor)

        if len(effective_echoes) == 0:
            return [],[]
        
        start = time.time()
        pulse_num = len(config.gt_intervals) + 1
        if pulse_num >= 2:
            # Fingerprinting搭載の場合
            certified_echoes: list[EchoGroup] = []
            error = config.torelance_error.in_nanoseconds
            peaks = np.array([x.peak_position for x in effective_echoes])
            for i in range(len(effective_echoes) - pulse_num + 1):
                min_remain_time = config.gt_intervals[-1] - error
                if peaks[i] + min_remain_time > len(signal):
                    # これ以上は認証を突破できないので終了
                    break
                certified = True
                fingerprint_echoes: list[Echo] = [effective_echoes[i]]
                first_echo_amp = effective_echoes[i].peak_height
                for pulse_index in range(pulse_num - 1):
                    base_position = config.gt_intervals[pulse_index]
                    # 範囲内のエコーを探す
                    applicable_echoes = np.flatnonzero(
                        np.abs(base_position + peaks[i] - peaks) <= error
                    )
                    if len(applicable_echoes) == 0:
                        # 該当するエコーがない場合は認証失敗
                        certified = False
                        break
                    elif config.consider_amp:
                        selected_echo = None
                        for a_echo in applicable_echoes:
                            actual_ratio = effective_echoes[a_echo].peak_height / first_echo_amp
                            ideal_ratio = config.gt_amps_ratio[pulse_index+1] / config.gt_amps_ratio[0]
                            if abs(actual_ratio - ideal_ratio) <= config.amp_torelance_error_ratio:
                                selected_echo = a_echo
                                break
                        if selected_echo is None:
                            # 振幅が合わない場合は認証失敗
                            certified = False
                            break
                        fingerprint_echoes.append(effective_echoes[selected_echo])
                    else:
                        # 振幅を考慮しない場合、最も近いエコーを選択
                        selected_echo = applicable_echoes[0]
                        fingerprint_echoes.append(effective_echoes[selected_echo])
                if certified:
                    certified_echoes.append(EchoGroup(fingerprint_echoes))

            effective_echoes_group = certified_echoes
        else:
            effective_echoes_group = [EchoGroup([x]) for x in effective_echoes]
        self.fingerprint_time_accum += time.time() - start
        
        if len(effective_echoes_group) == 0:
            return [],[]
        
        # ピークが大きい順、サンプル位置が小さい順にソートして最大10個取得
        start = time.time()
        effective_echoes_group.sort(key=lambda x: (-x[0].peak_height, x[0].peak_position))
        effective_echoes_group = effective_echoes_group[:10] if len(effective_echoes_group) > 10 else effective_echoes_group
        self.sort_time_accum += time.time() - start

        # Strongest
        start = time.time()
        fired_pulse_height = config.gt_amps_ratio[0] * 9 if config.consider_amp else 9
        highest_peak = effective_echoes_group[0][0].peak_height / fired_pulse_height
        highest_peak_time = effective_echoes_group[0][0].peak_position - self.peak_offset

        distance_m = highest_peak_time * 0.15
        # if distance_m < self.min_distance:
        #     return [],[]
        intensity = int(min(highest_peak * 255, 255))
        alpha = np.deg2rad(config.azimuth / 100.0)
        omega = np.deg2rad(config.altitude / 100.0)
        x = distance_m * np.cos(alpha) * np.cos(omega)
        y = - distance_m * np.sin(alpha) * np.cos(omega)
        z = - distance_m * np.sin(omega)

        self.calc_pcd_time_accum += time.time() - start

        return [
            VeloPoint(
                intensity=intensity,
                channel=0,
                timestamp=config.start_timestamp.in_nanoseconds,
                azimuth=config.azimuth,
                altitude=config.altitude,
                distance_m=distance_m,
                x=x,
                y=y,
                z=z,
            )
        ], effective_echoes_group


def detect_echo(signal: npt.NDArray[np.float64], thd_factor: float = 1.0, show_plot: bool = False) -> list[Echo]:
    # ----------------------- パラメータ計算 -----------------------
    # ヒストグラムの平均値B1
    b_one = float(np.mean(signal))

    # エコー判定閾値
    echo_judgment_threshold1 = b_one + (4.5 - b_one * 0.5) * thd_factor # b_one * 0.5 + 4.5
    echo_judgment_threshold2 = b_one + np.sqrt(b_one * (9 - b_one)) * thd_factor

    # 判定閾値を切り替えるサンプル位置
    echo_judgement_position = 100

    # エコー検出閾値
    echo_detection_threshold = b_one

    # エコー幅閾値
    echo_width_threshold = 0

    # 谷判定閾値
    valley_threshold = 1 # 10

    if show_plot:
        plt.figure(figsize=(12, 4))
        plt.cla()
        plt.plot(signal, color='blue')

        plt.hlines(y=echo_judgment_threshold1, xmin=0, xmax=echo_judgement_position, color='red', linestyle='--')
        plt.hlines(y=echo_judgment_threshold2, xmin=echo_judgement_position, xmax=len(signal), color='red', linestyle='--')
        # plt.axhline(y=echo_detection_threshold, color='red', linestyle='--')
        # plt.axvline(x=echo_judgement_position, color='red', linestyle='--')

    # ----------------------- エコー検出 -----------------------
    # ピーク検出
    peaks_global = np.hstack([
        find_peaks(signal[:echo_judgement_position], height=echo_judgment_threshold1)[0],
        find_peaks(signal[echo_judgement_position:], height=echo_judgment_threshold2)[0] + echo_judgement_position
    ])
    peaks_binary = np.zeros_like(signal)
    peaks_binary[peaks_global] = signal[peaks_global]

    if show_plot:
        plt.scatter(peaks_global, peaks_binary[peaks_global], color='green')

    # エコー検出閾値以上の連続するサンプル位置を取得
    raises = np.flatnonzero(
        (signal[:-1] < echo_detection_threshold) & (signal[1:] >= echo_detection_threshold)
    ) + 1
    falls = np.flatnonzero(
        (signal[:-1] >= echo_detection_threshold) & (signal[1:] < echo_detection_threshold)
    ) + 1
    if len(raises) == 0 and len(falls) == 0:
        return [] # エコーが検出されなかった場合
    elif len(raises) == 0 or raises[0] > falls[0]:
        raises = np.insert(raises, 0, 0)
    elif len(falls) == 0 or raises[-1] > falls[-1]:
        falls = np.append(falls, len(signal) - 1)
    
    effective_echoes: list[Echo] = []
    for echo_start, echo_end in zip(raises, falls):
        sig_echo = signal[echo_start:echo_end]

        if show_plot:
            plt.hlines(y=echo_detection_threshold, xmin=echo_start, xmax=echo_end, color='green', linestyle='--')

        # エコー内のピーク位置を取得
        peaks_local = np.flatnonzero(peaks_binary[echo_start:echo_end])
        if len(peaks_local) == 0:
            continue

        # 谷が存在したらエコーを分割
        split_positions = []
        for i in range(len(peaks_local)-1):
            if sig_echo[peaks_local[i+1]] - np.min(sig_echo[peaks_local[i]:peaks_local[i+1]]) > valley_threshold:
                split_positions.append(np.argmin(sig_echo[peaks_local[i]:peaks_local[i+1]]) + peaks_local[i])
                if show_plot:
                    plt.axvline(x=split_positions[-1]+echo_start, color='purple', linestyle='--')
        candidate_echo_range_list = []
        if len(split_positions) == 0:
            candidate_echo_range_list.append((0, len(sig_echo)))
        else:
            split_positions = [0] + split_positions + [len(sig_echo)]
            for i in range(len(split_positions)-1):
                candidate_echo_range_list.append((split_positions[i],split_positions[i+1]))

        for c_echo_start, c_echo_end in candidate_echo_range_list:
            peaks_range = peaks_binary[echo_start+c_echo_start:echo_start+c_echo_end]
            peak_position = int(np.argmax(peaks_range) + echo_start + c_echo_start)
            peak_height = signal[peak_position]
            width = c_echo_end - c_echo_start
            if width >= echo_width_threshold:
                effective_echoes.append(Echo(peak_position, peak_height, width))

            if show_plot:
                plt.hlines(y=echo_detection_threshold+0.5, xmin=echo_start+c_echo_start, xmax=echo_start+c_echo_end, color='orange', linestyle='--')
                plt.scatter(peak_position, peak_height + 0.1, color='orange')

    if show_plot:
        plt.show()

    return effective_echoes
