import asyncio

from prometheus_client import generate_latest, CONTENT_TYPE_LATEST, start_http_server
from aiohttp import web

from typing import Optional


class API:
    def __init__(self, loop: Optional[asyncio.AbstractEventLoop] = None):
        if not loop:
            loop = asyncio.get_event_loop()
        self.loop = loop
        self.app = web.Application(loop=self.loop)
        self.app.router.add_get('/metrics', self.metrics, name='metrics')

    async def start(self):
        start_http_server(8000)
        runner = web.AppRunner(self.app)
        await runner.setup()
        site = web.TCPSite(runner=runner, host='0.0.0.0', port=8080)
        await site.start()

    async def metrics(self, request: web.Request):
        return web.Response(body=generate_latest(), content_type='text/plain; version=0.0.4;')
