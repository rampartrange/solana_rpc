import asyncio
import json

from websockets import connect, ConnectionClosed

from api import API
from event_handler import BaseEventHandler, GetSupplyHandler
from models import EventType, BaseMethodResponse
from db import MongoDB
from priority_queue import LatestTimestampQueue
from utils import init_logger
from settings import Settings

_log = init_logger(__name__)


class EventListener:
    def __init__(self, handler: BaseEventHandler):
        self.api = API()
        self.handler = handler
        self._settings = Settings()
        self._db = MongoDB(self._settings.MONGO_URI, self._settings.MONGO_DB)
        self._task_queue = asyncio.Queue()
        self._result_queue = LatestTimestampQueue(max_size=self._settings.MAX_QUEUE_SIZE)

    async def start(self):
        _log.info("Starting event listener")
        tasks = [asyncio.create_task(self.api.start()),
                 asyncio.create_task(self.event_consumer(self._settings.WEBSOCKET_URI)),
                 asyncio.create_task(self.event_processor(self.handler))]

        await asyncio.gather(*tasks)

    async def event_consumer(self, uri):
        while True:
            try:
                async with connect(uri) as websocket:
                    try:
                        while True:
                            data = await websocket.recv()
                            await self._task_queue.put(data)
                    except Exception as e:
                        _log.error(f"WebSocket error: {e}")
            except ConnectionClosed as e:
                _log.error(f"WebSocket connection closed: {e.code} ({e.reason})")
                await asyncio.sleep(5)
            except Exception as e:
                _log.error(f"WebSocket error: {e}")
                await asyncio.sleep(5)

    async def event_processor(self, handler: BaseEventHandler):
        while True:
            data = await self._task_queue.get()
            event = json.loads(data)['type']

            if event == EventType.INVOKE:
                _log.info("Invoke event received")
                resp = await handler.handle_event()
                await self._store_response(resp)
                _log.info("Invoke event processed")
            elif event == EventType.ERROR:
                _log.info("Error event received")
            elif event == EventType.NOTHING:
                continue
            else:
                _log.info(f"Unknown message received: {data}")
            self._task_queue.task_done()

    def get_latest_response(self):
        return self._result_queue.get_latest()

    async def _store_response(self, response: BaseMethodResponse):
        self._result_queue.put(response)
        self._db.store_response(response)


async def main():
    event_listener = EventListener(handler=GetSupplyHandler())
    await event_listener.start()


if __name__ == '__main__':
    asyncio.run(main())
