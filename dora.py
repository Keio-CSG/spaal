from spaal2 import DummyLidarVLP16, DummyOutdoor, DummySpooferArb, visualize, PreciseDuration
import gen3d
import genpulse
import numpy as np


def main():
    # generate arb
    csv = "out/dora_csv.csv"

    masked_image = gen3d.Masked3dImage.from_csv(csv)
    pulse, period = genpulse.gen_pulse_from_csv_agilent_fast(
        data=masked_image,
        first_laser_id=10,
        sample_ns=64,
    )
    pulse = np.where(pulse > 0.5, 1.0, 0.0)

    lidar = DummyLidarVLP16()
    outdoor = DummyOutdoor()
    spoofer = DummySpooferArb(pulse, PreciseDuration(nanoseconds=period), PreciseDuration(nanoseconds=2400))

    point_list = []
    while True:
        try:
            config, signal = lidar.scan()

            if config.altitude == 900 and abs(config.azimuth - 100) < 20:
                spoofer.trigger(config, signal)

            signal = outdoor.apply(signal)
            signal += spoofer.get_range_signal(config.start_timestamp, config.accept_duration)
            points = lidar.receive(config, signal)
            point_list.extend(points)
        except StopIteration:
            break

    print(f"There are {len(point_list)} points.")
    visualize(point_list)


if __name__ == "__main__":
    main()
