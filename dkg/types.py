from typing import NewType, TypeVar, Any
from dataclasses import dataclass


URI = NewType("URI", str)


@dataclass
class BlockchainEndpoint:
    pass


@dataclass
class NodeEndpoint:
    method: str
    path: str


BlockchainResponse = Any
NodeResponse = Any

TReturn = TypeVar('TReturn')
