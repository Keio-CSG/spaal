from .precise_duration import PreciseDuration


class MeasurementConfig:
    """
    LiDAR測距の設定を保持するクラス
    """
    def __init__(self, 
                 start_timestamp: PreciseDuration, 
                 accept_duration: PreciseDuration, 
                 azimuth: int, 
                 altitude: int,
                 torelance_error: PreciseDuration = PreciseDuration(nanoseconds=0),
                 gt_intervals: list[int] = [],
                 consider_amp: bool = False,
                 gt_amps_ratio: list[float] = [],
                 amp_torelance_error_ratio: float = 0.0):
        """
        Parameters
        ----------
        start_timestamp : PreciseDuration
            測距の開始時刻
        accept_duration : PreciseDuration
            測距でPDを有効にしておく時間間隔
        azimuth : int
            測距している方位角(0.01deg)
        altitude : int
            測距している仰角(0.01deg)
        torelance_error : PreciseDuration, optional
            測距の許容誤差, by default PreciseDuration(nanoseconds=0)
        gt_intervals : list[int], optional
            複数パルスを発射するときの、2つ目以降のパルスの発射タイミング(ns)
            1つしかパルスを発射しない場合は空リスト, by default []
        consider_amp : bool, optional
            振幅変調を使っているかどうか, by default False
        gt_amps_ratio : list[float], optional
            振幅変調でのそれぞれのパルスの振幅比率, by default []
        amp_torelance_error_ratio : float, optional
            振幅変調での振幅比率の許容誤差, by default 0.0
        """
        self.start_timestamp = start_timestamp
        self.accept_duration = accept_duration
        self.azimuth = azimuth
        self.altitude = altitude
        self.torelance_error = torelance_error
        self.gt_intervals = gt_intervals
        self.consider_amp = consider_amp
        self.gt_amps_ratio = gt_amps_ratio
        self.amp_torelance_error_ratio = amp_torelance_error_ratio
