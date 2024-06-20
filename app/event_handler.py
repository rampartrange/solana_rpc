import aiohttp

from typing import Any
from prometheus_client import Histogram

from models import GetSupplyResponse, BaseMethodResponse
from utils import now_ms


class BaseEventHandler:
    base_url = "https://api.devnet.solana.com"

    async def handle_event(self) -> BaseMethodResponse:
        """Serializes event and tracks latency"""
        raise NotImplementedError()

    async def _fetch(self, payload: dict[str, Any]) -> (dict[str, Any], int):
        """Fetch data from API and calculate latency"""
        start_time = now_ms()
        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url, json=payload) as resp:
                result = await resp.json()
                result = result['result']
                latency = now_ms() - start_time

                return result, latency


class GetSupplyHandler(BaseEventHandler):

    def __init__(self):
        self.latency_metric = Histogram(
            name='getSupply_latency_ms',
            documentation='Latency of getSupply requests in ms',
            buckets=[100, 200, 300, 400, 500, 600, 700, 800, 900, 1000]
        )

    async def handle_event(self) -> GetSupplyResponse:
        payload = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "getSupply",
            "params": []
        }
        data, latency = await self._fetch(payload)
        self.latency_metric.observe(latency)
        return GetSupplyResponse(latency=latency, **data)
