class VeloPoint:
    def __init__(self, intensity: int, channel: int, timestamp: int, azimuth: int, altitude: int, distance_m: float, x: float, y: float, z: float) -> None:
        self.intensity = intensity
        self.channel = channel
        self.timestamp = timestamp
        self.azimuth = azimuth
        self.altitude = altitude
        self.distance_m = distance_m
        self.x = x
        self.y = y
        self.z = z
