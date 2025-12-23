"""Minimal psutil stub for testing environments."""


class _MemoryInfo:
    rss = 0
    vms = 0


class Process:
    def __init__(self, pid=None):
        self.pid = pid

    def memory_info(self):
        return _MemoryInfo()


def ProcessInfo():
    return Process()


__all__ = ["Process"]
