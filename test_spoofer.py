from spaal2 import DummySpooferContinuousPulse, PreciseDuration

import matplotlib.pyplot as plt

spoofer = DummySpooferContinuousPulse(frequency=1 * 1e6, pulse_width=PreciseDuration(nanoseconds=50))

out = spoofer.get_range_signal(PreciseDuration(nanoseconds=700), PreciseDuration(nanoseconds=1000))

plt.plot(out)
plt.show()
