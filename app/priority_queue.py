import queue
from typing import Optional
from dataclasses import dataclass, field

from models import BaseMethodResponse


@dataclass(order=True)
class PriorityQueueItem:
    priority: int
    item: BaseMethodResponse = field(compare=False)


class LatestTimestampQueue:
    def __init__(self, max_size: int):
        self._queue = queue.PriorityQueue()
        self._max_size = max_size

    def put(self, item: BaseMethodResponse):
        priority = -item.timestamp
        self._queue.put(PriorityQueueItem(priority, item))
        if self._queue.qsize() >= self._max_size:
            self._trim_queue()

    def get_latest(self) -> Optional[BaseMethodResponse]:
        try:
            while True:
                comparable_item = self._queue.get_nowait()
                latest_item = comparable_item.item
                self._queue.task_done()
                if latest_item.timestamp == -comparable_item.priority:
                    return latest_item
        except queue.Empty:
            return None

    def _trim_queue(self):
        with self._queue.mutex:
            max_item = self._queue.get()
            self._queue.queue.clear()
            self._queue.put(max_item)

    def clear(self):
        with self._queue.mutex:
            self._queue.queue.clear()

