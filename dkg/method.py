from dkg._utils.node_request import NodeEndpoint
from dkg._utils.blockchain_request import BlockchainEndpoint
from dkg.dataclasses import HTTPRequestMethod
from dkg.exceptions import HTTPRequestMethodNotSupported, ValidationError
from dkg.types import TFunc
from typing import Generic, Type, TYPE_CHECKING, Any
from dkg._utils.string_transformations import snake_to_camel
import itertools

if TYPE_CHECKING:
    from dkg.module import Module


class Method(Generic[TFunc]):
    def __init__(self, endpoint: BlockchainEndpoint | NodeEndpoint):
        self.endpoint = endpoint

    def __get__(
        self, obj: 'Module | None' = None, _: Type['Module'] | None = None
    ) -> TFunc:
        if obj is None:
            raise TypeError(
                'Direct calls to methods are not supported. '
                'Methods must be called from an module instance, '
                'usually attached to a dkg instance.'
            )
        return obj.retrieve_caller_fn(self)

    def process_args(self, *args: Any, **kwargs: dict[str, Any]):
        match self.endpoint:
            case NodeEndpoint():
                if self.endpoint.method == HTTPRequestMethod.GET:
                    required_args = self.endpoint.params
                elif self.endpoint.method == HTTPRequestMethod.POST:
                    required_args = self.endpoint.data
                else:
                    raise HTTPRequestMethodNotSupported(
                        f"{self.endpoint.method.name} method isn't supported"
                    )

                if len(args) > len(required_args):
                    raise ValidationError(
                        "Number of positional arguments can't be bigger than "
                        "number of required arguments"
                    )

                args_mapped = dict(zip(itertools.islice(required_args.keys(), len(args)), args))
                camel_kwargs = {snake_to_camel(key): value for key, value in kwargs.items()}

                processed_args = {}
                processed_args.update(args_mapped)
                processed_args.update(camel_kwargs)

                if any(missing_params := (arg not in processed_args for arg in required_args)):
                    raise ValidationError(
                        f"Missing required arg(s): {', '.join(missing_params)}"
                    )

                return {
                    'params': processed_args
                    if self.endpoint.method == HTTPRequestMethod.GET
                    else {},
                    'data': processed_args
                    if self.endpoint.method == HTTPRequestMethod.POST
                    else {},
                }
            case _:
                return {}
