import numpy as np

# def gen_sunlight(length: int, center: float, width: float) -> np.ndarray:
#     y = np.random.rand(length//2 + 10)
#     x = np.arange(0, length//2 + 10)
#     y2 = 3000 - 20 * x
#     y2[140:] = 300 - x[140:] / 3

#     amp = y * y2

#     angle = np.random.rand(length//2 + 10) * 6.28 - 3.14

#     signal = np.fft.irfft(amp * np.exp(angle * 1.j)) * width / 20 + center
#     return signal[:length]

def gen_sunlight(length: int, mean: float) -> np.ndarray:
    slope = 0.48
    intercept = 0.029

    sunlight_mean = mean * 166
    sunlight_std = 10 ** (slope * np.log10(sunlight_mean) + intercept)

    x = np.arange(0, length//2 + 10)
    amp_amp = 1300 - 20 * x
    amp_amp[55:] = 237 - 2/3 * x[55:]

    amp = np.random.rand(length//2 + 10) * amp_amp

    angle = np.random.rand(length//2 + 10) * 2 * np.pi - np.pi

    synth_signal = np.fft.irfft(amp * np.exp(1j * angle)) * sunlight_std / 5.17 + sunlight_mean
    return np.clip(synth_signal, 0, 1497)[:length] / 166

def gen_sunlight2(length: int, mean: float) -> np.ndarray:
    slope = 0.48
    intercept = 0.029

    sunlight_mean = mean
    sunlight_std = 10 ** (slope * np.log10(sunlight_mean) + intercept)

    x = np.arange(0, length//2 + 10)
    amp_amp = 1300 - 20 * x
    amp_amp[55:] = 237 - 2/3 * x[55:]

    amp = np.random.rand(length//2 + 10) * amp_amp

    angle = np.random.rand(length//2 + 10) * 2 * np.pi - np.pi

    synth_signal = np.fft.irfft(amp * np.exp(1j * angle)) * sunlight_std / 5.17 + sunlight_mean
    return np.clip(synth_signal, 0, 1497)[:length]