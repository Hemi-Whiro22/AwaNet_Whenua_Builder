"""Lightweight stub of prometheus_client for offline runs."""


class Counter:
    def __init__(self, *args, **kwargs) -> None:
        self._count = 0

    def inc(self, value: float = 1.0) -> None:
        self._count += value


class Histogram:
    def __init__(self, *args, **kwargs) -> None:
        self._values = []

    def observe(self, value: float) -> None:
        self._values.append(value)


__all__ = ["Counter", "Histogram"]
