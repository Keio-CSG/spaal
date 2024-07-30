from typing import Optional
from typing import List
from abc import ABC, abstractmethod
import math
import numpy as np
import numpy.typing as npt
from .precise_duration import PreciseDuration
from .measurement_config import MeasurementConfig
import matplotlib.pyplot as plt
import pandas as pd
# from .dummy_spoofer import DummySpooferInterface


class DummySpooferInterface(ABC):
    @abstractmethod
    def trigger(self, config: MeasurementConfig, signal: npt.NDArray[np.float64]):
        pass

    @abstractmethod
    def get_range_signal(self, start_timestamp: PreciseDuration, duration: PreciseDuration) -> npt.NDArray[np.float64]:
        pass

# nagai 0726
#class RealSpoofer(DummySpooferInterface):
#    def __init__(self, csv_file: str, column: str, rows: list, remove_max: bool = True) -> None:
#        self.csv_file = csv_file
#        self.column = column
#        self.rows = rows
#        self.remove_max = remove_max
#        self.trigger_time: Optional[int] = None
#
#        # Load and process the histogram data from the CSV
#        self.hist_data = self._load_histogram_data()
#
#    def _load_histogram_data(self):
#        # Load the data from the CSV
#        df = pd.read_csv(self.csv_file)
#
#        # Select the specified column and rows
#        data = df[self.column].iloc[self.rows].values
#
#        # Remove the maximum value if specified
#        if self.remove_max:
#            max_value = np.max(data)
#            data = data[data != max_value]
#
#        return data
#
#    def trigger(self, config, signal):
#        # Placeholder implementation, real implementation may vary
#        self.trigger_time = config.start_timestamp
#
#    def get_range_signal(self, start_timestamp, duration):
#        if self.trigger_time is None:
#            return np.zeros(duration.in_nanoseconds)
#
  #      # Generate the spoofer signal based on the histogram data
 #       signal_length = len(self.hist_data)
#        start_index = start_timestamp - self.trigger_time
#
 #       if start_index < 0 or start_index >= signal_length:
#            return np.zeros(duration.in_nanoseconds)
#
#        end_index = min(start_index + duration, signal_length)
#        return self.hist_data[start_index:end_index]

# Example usage
# spoofer = RealSpoofer(csv_file='data.csv', column='Histogram', rows=range(100, 200))
# config = MeasurementConfig(start_timestamp=0)
# spoofer.trigger(config, np.zeros(100))
# signal = spoofer.get_range_signal(10, 50)
# print(signal)

class RealSpoofer(DummySpooferInterface):
    def __init__(self, csv_file: str, column: str, rows: list, remove_max: bool = True) -> None:
        self.csv_file = csv_file
        self.column = column
        self.rows = rows
        self.remove_max = remove_max
        self.trigger_time: Optional[int] = None

        # Load and process the histogram data from the CSV
        self.hist_data = self._load_histogram_data()

    def _load_histogram_data(self):
        # Load the data from the CSV
        df = pd.read_csv(self.csv_file)

        # Select the specified column and rows
        data = df[self.column].iloc[self.rows].values

        # Remove the maximum value if specified
        if self.remove_max:
            max_value = np.max(data)
            data = data[data != max_value]

        return data

    def trigger(self, config, signal):
        # Placeholder implementation, real implementation may vary
        self.trigger_time = config.start_timestamp.in_nanoseconds

    def get_range_signal(self, start_timestamp, duration):
        if self.trigger_time is None:
            return np.zeros(duration.in_nanoseconds)

        # Generate the spoofer signal based on the histogram data
        signal_length = len(self.hist_data)
        start_index = start_timestamp.in_nanoseconds - self.trigger_time

        if start_index < 0:
            start_index = 0

        end_index = start_index + duration.in_nanoseconds

        # Calculate how many times we need to repeat the hist_data
        repeat_count = (end_index - start_index) // signal_length + 1

        # Repeat the hist_data and truncate it to the required length
        repeated_data = np.tile(self.hist_data, repeat_count)
        signal = repeated_data[start_index:end_index]

        return signal


class DummySpooferOff(DummySpooferInterface):
    """
    何もしないSpoofer
    """
    def __init__(self) -> None:
        pass

    def trigger(self, config: MeasurementConfig, signal: npt.NDArray[np.float64]):
        pass

    def get_range_signal(self, start_timestamp: PreciseDuration, duration: PreciseDuration) -> npt.NDArray[np.float64]:
        return np.zeros((duration.in_nanoseconds, ))


class DummySpooferContinuousPulse(DummySpooferInterface):
    def __init__(self, frequency: float, pulse_width: PreciseDuration, csv_file: str, column: str, start_row: int, end_row: int, debug: bool = False) -> None:
        self.frequency = frequency
        self.pulse_width = pulse_width
        self.pulse_period_ns = math.floor(1 / self.frequency * 1e9)
        self.debug = debug

        # サブセグメントを取得
        self.sub_segments = self.extract_sub_segments(csv_file, column, start_row, end_row)
        
        if self.debug:
            print(f"Spoofer: Continuous Pulse")
            print(f"\tfrequency: {self.frequency / 1e6} MHz")
            print(f"\tpulse_width: {self.pulse_width}")
        
        # サブセグメントをバッファに展開
        max_duration = PreciseDuration(nanoseconds=5000)
        self.pulse_sequence_buffer = np.tile(
            np.concatenate(self.sub_segments), 
            math.ceil(max_duration.in_nanoseconds / len(self.sub_segments[0]))
        )

    def extract_sub_segments(self, csv_file: str, column: str, start_row: int, end_row: int) -> List[np.ndarray]:
        def extract_segments(data):
            non_zero_indices = [i for i, x in enumerate(data) if x != 0]
            if not non_zero_indices:
                return [], []
            start_idx = non_zero_indices[0]
            end_idx = non_zero_indices[-1] + 1
            data = data[start_idx:end_idx]

            main = []
            subs = []
            current_segment = []
            in_main = False
            
            for i, value in enumerate(data):
                if value > 0:
                    current_segment.append(value)
                    if value == max(data):
                        in_main = True
                else:
                    if current_segment:
                        if i == 0 or data[i-1] != 0:
                            current_segment.insert(0, 0)
                        if i == len(data) - 1 or data[i+1] != 0:
                            current_segment.append(0)
                        if in_main:
                            main.append(current_segment)
                            in_main = False
                        else:
                            subs.append(current_segment)
                        current_segment = []

            if current_segment:
                current_segment.append(0)
                if in_main:
                    main.append(current_segment)
                else:
                    subs.append(current_segment)

            return main, subs

        df = pd.read_csv(csv_file)
        all_subs = []

        for row in range(start_row, end_row + 1):
            data_str = df[column].iloc[row]
            data = list(map(int, data_str.split()))
            _, subs = extract_segments(data)
            all_subs.extend(subs)
        
        return all_subs

    def trigger(self, config: MeasurementConfig, signal: npt.NDArray[np.float64]):
        pass

    def get_range_signal(self, start_timestamp: PreciseDuration, duration: PreciseDuration) -> npt.NDArray[np.float64]:
        phase = start_timestamp.in_nanoseconds % len(self.pulse_sequence_buffer)
        end_index = phase + duration.in_nanoseconds
        if end_index > len(self.pulse_sequence_buffer):
            return np.concatenate([
                self.pulse_sequence_buffer[phase:],
                self.pulse_sequence_buffer[:end_index % len(self.pulse_sequence_buffer)]
            ])
        else:
            return self.pulse_sequence_buffer[phase:end_index]




class DummySpooferArb(DummySpooferInterface):
    def __init__(self, arb: npt.NDArray[np.float64], period: PreciseDuration, delay: PreciseDuration) -> None:
        self.distance_m = 10.0
        self.trigger_time: Optional[PreciseDuration] = None
        self.arb = arb
        self.period = period
        self.period_per_sample = int(period.in_nanoseconds // arb.size)
        self.delay = delay

    def trigger(self, config: MeasurementConfig, signal: npt.NDArray[np.float64]):
        if self.trigger_time is not None:
            return

        # delay
        new_signal = np.zeros_like(signal)
        delay = int(self.distance_m / 0.15)
        new_signal[delay:] = signal[:-delay]
        signal = new_signal

        # find the first peak
        raises = np.flatnonzero(
            (signal[:-1] < 0.5) & (signal[1:] >= 0.5)
        ) + 1
        if raises.size == 0:
            return
        peak_index = raises[0]
        peak_time = config.start_timestamp + PreciseDuration(nanoseconds=peak_index)

        self.trigger_time = peak_time
        print(f"Triggered at {self.trigger_time.in_nanoseconds}ns")

    def _get_arb_data_in_ns(self, duration: PreciseDuration) -> float:
        if duration.is_negative or duration >= self.period:
            return 0.0

        return self.arb[math.floor(duration.in_nanoseconds / self.period_per_sample)]

    def get_range_signal(self, start_timestamp: PreciseDuration, duration: PreciseDuration) -> npt.NDArray[np.float64]:
        if self.trigger_time is None:
            return np.zeros((duration.in_nanoseconds, ))

        arb_start = self.trigger_time + self.delay + PreciseDuration(nanoseconds=int(self.distance_m / 0.15))
        arb_end = arb_start + self.period
        if start_timestamp >= arb_end:
            self.trigger_time = None
            return np.zeros((duration.in_nanoseconds, ))

        if start_timestamp >= arb_start and start_timestamp + duration <= arb_end:
            # in the middle of the arb
            start_index_ns = (start_timestamp - arb_start).in_nanoseconds
            arb_start_index = math.floor(start_index_ns / self.period_per_sample)
            arb_end_index = math.floor((start_index_ns + duration.in_nanoseconds - 1) / self.period_per_sample)
            extended_arb = np.repeat(self.arb[arb_start_index:arb_end_index+1], self.period_per_sample)
            return extended_arb[start_index_ns - arb_start_index * self.period_per_sample:start_index_ns - arb_start_index * self.period_per_sample + duration.in_nanoseconds]

        result = np.zeros((duration.in_nanoseconds, ))
        for i in range(duration.in_nanoseconds):
            if start_timestamp + PreciseDuration(nanoseconds=i) >= arb_start:
                result[i] = self._get_arb_data_in_ns(start_timestamp + PreciseDuration(nanoseconds=i) - arb_start)
            else:
                result[i] = 0.0
        return result

class DummySpooferAdaptiveHFR(DummySpooferInterface):
    """
    Adaptive HFR Spoofer
    """
    def __init__(self, 
                 frequency: float,
                 duration: PreciseDuration,
                 spoofer_distance_m: float,
                 pulse_width: PreciseDuration,
                 debug: bool = False) -> None:
        """
        Parameters
        ----------
        frequency : float
            パルスの周波数(Hz)
        duration : PreciseDuration
            トリガーされてからの攻撃継続時間
        spoofer_distance_m : float
            SpooferとLiDARの距離(m)
        pulse_width : PreciseDuration
            パルスの幅
        debug : bool, optional
            デバッグ情報を表示するかどうか, by default False
        """
        self.frequency = frequency
        self.duration = duration
        self.distance_m = spoofer_distance_m
        self.pulse_width = pulse_width
        self.pulse_period_ns = math.floor(1 / self.frequency * 1e9)
        self.trigger_time: Optional[PreciseDuration] = None
        if debug:
            print(f"Spoofer: Adaptive HFR")
            print(f"\tfrequency: {self.frequency / 1e6} MHz")
            print(f"\tduration: {self.duration}")
            print(f"\tpulse_width: {self.pulse_width}")

        # パルス形状を事前計算
        sigma = pulse_width.in_nanoseconds / (2 * np.sqrt(2 * np.log2(2)))
        pulse_x = np.arange(-3 * sigma, 3 * sigma, 1.0)
        # ガウス分布
        pulse_shape = 9 * np.exp(-((pulse_x) ** 2) / (2 * sigma ** 2))
        one_pulse_sequence = np.zeros((self.pulse_period_ns, ))
        one_pulse_sequence[:pulse_shape.size] = pulse_shape

        # 5000nsのバッファを事前計算し、必要な部分だけを逐一切り出すようにする
        max_duration = PreciseDuration(nanoseconds=5000)
        self.pulse_sequence_buffer = np.tile(
            one_pulse_sequence, 
            math.ceil(max_duration.in_nanoseconds / self.pulse_period_ns)
        )

    def trigger(self, config: MeasurementConfig, signal: npt.NDArray[np.float64]):
        if self.trigger_time is not None:
            return
        
        # delay
        new_signal = np.zeros_like(signal)
        delay = int(self.distance_m / 0.15)
        new_signal[delay:] = signal[:-delay]
        signal = new_signal

        # find the first peak
        raises = np.flatnonzero(
            (signal[:-1] < 0.5) & (signal[1:] >= 0.5)
        ) + 1
        if raises.size == 0:
            return
        peak_index = raises[0]
        peak_time = config.start_timestamp + PreciseDuration(nanoseconds=peak_index)

        self.trigger_time = peak_time
        print(f"Triggered at {self.trigger_time.in_nanoseconds}ns")

    def get_range_signal(self, start_timestamp: PreciseDuration, duration: PreciseDuration) -> npt.NDArray[np.float64]:
        if self.trigger_time is None:
            return np.zeros((duration.in_nanoseconds, ))
        
        attack_start_time = self.trigger_time
        attack_end_time = self.trigger_time + self.duration
        if start_timestamp + duration <= attack_start_time:
            return np.zeros((duration.in_nanoseconds, ))
        if start_timestamp >= attack_end_time:
            self.trigger_time = None
            return np.zeros((duration.in_nanoseconds, ))
        
        phase = (start_timestamp - attack_start_time).in_nanoseconds % self.pulse_period_ns
        signal = self.pulse_sequence_buffer[phase:phase+duration.in_nanoseconds]
        if start_timestamp < attack_start_time:
            signal[:attack_start_time.in_nanoseconds - start_timestamp.in_nanoseconds] = 0.0
        if start_timestamp + duration > attack_end_time:
            signal[attack_end_time.in_nanoseconds - start_timestamp.in_nanoseconds:] = 0.0
        return signal

class DummySpooferAdaptiveHFRWithSpeculation(DummySpooferInterface):
    """
    Adaptive HFR Spoofer with Speculation
    """
    def __init__(self, 
                 frequency: float,
                 duration: PreciseDuration,
                 frame_interval: PreciseDuration,
                 spoofer_distance_m: float,
                 pulse_width: PreciseDuration,
                 debug: bool = False) -> None:
        """
        Parameters
        ----------
        frequency : float
            パルスの周波数(Hz)
        duration : PreciseDuration
            トリガーされてからの攻撃継続時間
        spoofer_distance_m : float
            SpooferとLiDARの距離(m)
        pulse_width : PreciseDuration
            パルスの幅
        debug : bool, optional
            デバッグ情報を表示するかどうか, by default False
        """
        self.frequency = frequency
        self.duration = duration
        self.frame_interval = frame_interval
        self.distance_m = spoofer_distance_m
        self.pulse_width = pulse_width
        self.pulse_period_ns = math.floor(1 / self.frequency * 1e9)
        self.trigger_time: Optional[PreciseDuration] = None
        self.speculated_trigger_time: Optional[PreciseDuration] = None
        if debug:
            print(f"Spoofer: Adaptive HFR")
            print(f"\tfrequency: {self.frequency / 1e6} MHz")
            print(f"\tduration: {self.duration}")
            print(f"\tpulse_width: {self.pulse_width}")

        # パルス形状を事前計算
        sigma = pulse_width.in_nanoseconds / (2 * np.sqrt(2 * np.log2(2)))
        pulse_x = np.arange(-3 * sigma, 3 * sigma, 1.0)
        # ガウス分布
        pulse_shape = 9 * np.exp(-((pulse_x) ** 2) / (2 * sigma ** 2))
        one_pulse_sequence = np.zeros((self.pulse_period_ns, ))
        one_pulse_sequence[:pulse_shape.size] = pulse_shape

        # 5000nsのバッファを事前計算し、必要な部分だけを逐一切り出すようにする
        max_duration = PreciseDuration(nanoseconds=5000)
        self.pulse_sequence_buffer = np.tile(
            one_pulse_sequence, 
            math.ceil(max_duration.in_nanoseconds / self.pulse_period_ns)
        )

    def trigger(self, config: MeasurementConfig, signal: npt.NDArray[np.float64]):
        if self.trigger_time is not None:
            return
        self.speculated_trigger_time = None
        
        # delay
        new_signal = np.zeros_like(signal)
        delay = int(self.distance_m / 0.15)
        new_signal[delay:] = signal[:-delay]
        signal = new_signal

        # find the first peak
        raises = np.flatnonzero(
            (signal[:-1] < 0.5) & (signal[1:] >= 0.5)
        ) + 1
        if raises.size == 0:
            return
        peak_index = raises[0]
        peak_time = config.start_timestamp + PreciseDuration(nanoseconds=peak_index)

        self.trigger_time = peak_time
        print(f"Triggered at {self.trigger_time.in_nanoseconds}ns")

    def get_range_signal(self, start_timestamp: PreciseDuration, duration: PreciseDuration) -> npt.NDArray[np.float64]:
        if self.trigger_time is None and self.speculated_trigger_time is None:
            return np.zeros((duration.in_nanoseconds, ))
        
        if self.trigger_time is not None:
            attack_start_time = self.trigger_time
        else:
            attack_start_time = self.speculated_trigger_time
        attack_end_time = attack_start_time + self.duration
        if start_timestamp + duration <= attack_start_time:
            return np.zeros((duration.in_nanoseconds, ))
        if start_timestamp >= attack_end_time:
            if self.trigger_time is not None:
                self.speculated_trigger_time = self.trigger_time + self.frame_interval
            elif self.speculated_trigger_time is not None:
                self.speculated_trigger_time += self.frame_interval
            self.trigger_time = None
            return np.zeros((duration.in_nanoseconds, ))
        
        phase = (start_timestamp - attack_start_time).in_nanoseconds % self.pulse_period_ns
        signal = self.pulse_sequence_buffer[phase:phase+duration.in_nanoseconds]
        if start_timestamp < attack_start_time:
            signal[:attack_start_time.in_nanoseconds - start_timestamp.in_nanoseconds] = 0.0
        if start_timestamp + duration > attack_end_time:
            signal[attack_end_time.in_nanoseconds - start_timestamp.in_nanoseconds:] = 0.0
        return signal
