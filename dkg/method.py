from dkg.types import BlockchainEndpoint, NodeEndpoint
from typing import TypeVar, Callable, Any, Generic, Type, TYPE_CHECKING

if TYPE_CHECKING:
    from dkg.module import Module

TFunc = TypeVar("TFunc", bound=Callable[..., Any])


class Method(Generic[TFunc]):
    def __init__(self, endpoint: BlockchainEndpoint | NodeEndpoint):
        self.endpoint = endpoint

    def __get__(
        self, obj: 'Module | None' = None, obj_type: Type['Module'] | None = None
    ) -> TFunc:
        if obj is None:
            raise TypeError(
                "Direct calls to methods are not supported. "
                "Methods must be called from an module instance, "
                "usually attached to a dkg instance."
            )
        return obj.retrieve_caller_fn(self)
