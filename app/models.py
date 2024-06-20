from dataclasses import dataclass, field
from enum import Enum
from typing import List

from utils import now_ms

__all__ = ["EventType", "BaseMethodResponse", "GetSupplyResponse"]


class EventType(str, Enum):
    INVOKE = "INVOKE"
    NOTHING = "NOTHING"
    ERROR = "ERROR"


@dataclass
class BaseMethodResponse:
    latency: int

    def __post_init__(self):
        self.timestamp = now_ms()

    def get_method_name(self) -> str:
        raise NotImplementedError()


@dataclass
class GetSupplyContext:
    slot: int


@dataclass
class GetSupplyValue:
    circulating: int
    nonCirculating: int
    nonCirculatingAccounts: List[str]
    total: int


@dataclass
class GetSupplyResponse(BaseMethodResponse):
    context: GetSupplyContext
    value: GetSupplyValue
    timestamp: int = field(init=False)

    def get_method_name(self) -> str:
        return "getSupply"
