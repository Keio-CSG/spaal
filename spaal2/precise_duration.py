from functools import total_ordering


@total_ordering
class PreciseDuration:
    """
    ナノ秒単位の時間間隔を表すクラス

    それ以外はDurationと同じ
    """
    nanoseconds_per_microsecond = 1000
    nanoseconds_per_millisecond = 1000 * nanoseconds_per_microsecond
    nanoseconds_per_second = 1000 * nanoseconds_per_millisecond
    nanoseconds_per_minute = 60 * nanoseconds_per_second
    nanoseconds_per_hour = 60 * nanoseconds_per_minute
    nanoseconds_per_day = 24 * nanoseconds_per_hour
    microseconds_per_millisecond = 1000
    microseconds_per_second = 1000 * microseconds_per_millisecond
    microseconds_per_minute = 60 * microseconds_per_second
    microseconds_per_hour = 60 * microseconds_per_minute
    microseconds_per_day = 24 * microseconds_per_hour
    milliseconds_per_second = 1000
    milliseconds_per_minute = 60 * milliseconds_per_second
    milliseconds_per_hour = 60 * milliseconds_per_minute
    milliseconds_per_day = 24 * milliseconds_per_hour
    seconds_per_minute = 60
    seconds_per_hour = 60 * seconds_per_minute
    seconds_per_day = 24 * seconds_per_hour
    minutes_per_hour = 60
    minutes_per_day = 24 * minutes_per_hour
    hours_per_day = 24

    def __init__(self, *, days: int = 0, hours: int = 0, minutes: int = 0, seconds: int = 0, milliseconds: int = 0, microseconds: int = 0, nanoseconds: int = 0):
        self._nanoseconds = nanoseconds
        self._nanoseconds += microseconds * self.nanoseconds_per_microsecond
        self._nanoseconds += milliseconds * self.nanoseconds_per_millisecond
        self._nanoseconds += seconds * self.nanoseconds_per_second
        self._nanoseconds += minutes * self.nanoseconds_per_minute
        self._nanoseconds += hours * self.nanoseconds_per_hour
        self._nanoseconds += days * self.nanoseconds_per_day

    @classmethod
    def zero(cls) -> "PreciseDuration":
        return cls(nanoseconds=0)

    @property
    def in_nanoseconds(self) -> int:
        return self._nanoseconds

    @property
    def in_microseconds(self) -> int:
        return self._nanoseconds // self.nanoseconds_per_microsecond

    @property
    def in_milliseconds(self) -> int:
        return self._nanoseconds // self.nanoseconds_per_millisecond

    @property
    def in_seconds(self) -> int:
        return self._nanoseconds // self.nanoseconds_per_second

    @property
    def in_minutes(self) -> int:
        return self._nanoseconds // self.nanoseconds_per_minute

    @property
    def in_hours(self) -> int:
        return self._nanoseconds // self.nanoseconds_per_hour

    @property
    def in_days(self) -> int:
        return self._nanoseconds // self.nanoseconds_per_day

    @property
    def is_negative(self) -> bool:
        return self._nanoseconds < 0

    def __hash__(self) -> int:
        return hash(self._nanoseconds)

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, PreciseDuration):
            return False
        return self._nanoseconds == __value._nanoseconds

    def __lt__(self, __value: object) -> bool:
        if not isinstance(__value, PreciseDuration):
            raise TypeError(f"'<' not supported between instances of 'PreciseDuration' and '{type(__value).__name__}'")
        return self._nanoseconds < __value._nanoseconds

    def __add__(self, __value: object) -> "PreciseDuration":
        if not isinstance(__value, PreciseDuration):
            raise TypeError(f"unsupported operand type(s) for +: 'PreciseDuration' and '{type(__value).__name__}'")
        return PreciseDuration(nanoseconds=self._nanoseconds + __value._nanoseconds)

    def __sub__(self, __value: object) -> "PreciseDuration":
        if not isinstance(__value, PreciseDuration):
            raise TypeError(f"unsupported operand type(s) for -: 'PreciseDuration' and '{type(__value).__name__}'")
        return PreciseDuration(nanoseconds=self._nanoseconds - __value._nanoseconds)

    def __mul__(self, __value: object) -> "PreciseDuration":
        if not isinstance(__value, int) and not isinstance(__value, float):
            raise TypeError(f"unsupported operand type(s) for *: 'PreciseDuration' and '{type(__value).__name__}'")
        return PreciseDuration(nanoseconds=int(self._nanoseconds * __value))

    def __truediv__(self, __value: object) -> "PreciseDuration":
        if not isinstance(__value, int) and not isinstance(__value, float):
            raise TypeError(f"unsupported operand type(s) for /: 'PreciseDuration' and '{type(__value).__name__}'")
        return PreciseDuration(nanoseconds=int(self._nanoseconds / __value))

    def __floordiv__(self, __value: object) -> "PreciseDuration":
        if not isinstance(__value, int) and not isinstance(__value, float):
            raise TypeError(f"unsupported operand type(s) for //: 'PreciseDuration' and '{type(__value).__name__}'")
        return PreciseDuration(nanoseconds=int(self._nanoseconds // __value))

    def __str__(self) -> str:
        return f"{self._nanoseconds} ns"
