import numpy as np
import numpy.typing as npt


class DummyOutdoor:
    """
    屋外環境をシミュレートするクラス
    """
    def __init__(self, wall_distance_m: float, reflectivity: float, debug: bool = False, sunlight: bool = False) -> None:
        """
        Parameters
        ----------
        wall_distance_m : float
            壁までの距離(m)
        reflectivity : float
            壁の反射率(0.0 ~ 1.0)
        debug : bool, optional
            デバッグ情報を表示するかどうか, by default False
        """
        self.wall_distance_m = wall_distance_m
        self.decay_rate = reflectivity
        self.sunlight = sunlight
        if debug:
            print(f"Outdoor:")
            print(f"\twall_distance_m: {self.wall_distance_m} m")
            print(f"\treflectivity: {self.decay_rate}")

    def apply(self, signal: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        """
        設定された屋外で反射して戻ってきた信号を計算

        Parameters
        ----------
        signal : npt.NDArray[np.float64]
            信号

        Returns
        -------
        npt.NDArray[np.float64]
            屋外で反射して戻ってきた信号
        """
        # decay
        signal = signal * self.decay_rate

        # shift
        shift_ns = int(self.wall_distance_m / 0.15)
        result = np.zeros_like(signal)
        result[shift_ns:] = signal[:-shift_ns]
        return result
