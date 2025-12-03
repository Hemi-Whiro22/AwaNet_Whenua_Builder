from typing import List

from shared.awa_bus.awa_events import AwaEvent

BUS: List[AwaEvent] = []


def emit(event: AwaEvent):
    BUS.append(event)


def latest(n: int = 10):
    return BUS[-n:]
