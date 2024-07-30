import numpy as np

def apply_noise(
        signal: np.ndarray, 
        min_value: float = 0, 
        max_value: float = 9, 
        ratio: float = 0.1) -> np.ndarray:
    """
    与えられた信号にノイズを付加する
    
    最大で(ratio * 100)%だけ信号が変動する

    Parameters
    ----------
    signal : np.ndarray
        信号
    min_value : float, optional
        信号の最小値, by default 0
    max_value : float, optional
        信号の最大値, by default 9
    ratio : float, optional
        ノイズの割合, by default 0.1

    Returns
    -------
    np.ndarray
        ノイズが付加された信号
    """
    noise = np.random.normal(0, ratio, len(signal))
    return np.clip(signal * (1 + noise), min_value, max_value)