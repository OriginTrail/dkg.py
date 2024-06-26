# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at

#   http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import itertools
import re
from typing import TYPE_CHECKING, Any, Generic, Type

from dkg.exceptions import ValidationError
from dkg.types import TFunc
from dkg.utils.blockchain_request import (
    ContractInteraction,
    ContractTransaction,
    JSONRPCRequest,
)
from dkg.utils.node_request import NodeCall
from dkg.utils.string_transformations import snake_to_camel

if TYPE_CHECKING:
    from dkg.module import Module


class Method(Generic[TFunc]):
    def __init__(self, action: JSONRPCRequest | ContractInteraction | NodeCall):
        self.action = action

    def __get__(
        self, obj: "Module | None" = None, _: Type["Module"] | None = None
    ) -> TFunc:
        if obj is None:
            raise TypeError(
                "Direct calls to methods are not supported. "
                "Methods must be called from a module instance, "
                "usually attached to a dkg instance."
            )
        return obj.retrieve_caller_fn(self)

    def process_args(self, *args: Any, **kwargs: Any):
        match self.action:
            case JSONRPCRequest():
                return {"args": self._validate_and_map(self.action.args, args, kwargs)}
            case ContractInteraction():
                contract = kwargs.pop("contract", None)
                if not self.action.contract:
                    if contract:
                        self.action.contract = contract
                    else:
                        raise ValidationError(
                            "ContractInteraction requires a 'contract' to be provided"
                        )

                return {
                    "args": self._validate_and_map(self.action.args, args, kwargs),
                    "state_changing": isinstance(self.action, ContractTransaction),
                }
            case NodeCall():
                return self._process_node_call_args(args, kwargs)
            case _:
                return {}

    def _validate_and_map(
        self,
        required_args: dict[str, Type] | Type,
        args: list[Any],
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        if not isinstance(required_args, dict):
            if (len(args) + len(kwargs)) != 1:
                raise ValidationError("Exactly one argument must be provided.")

            if len(args) == 1:
                return args[0]
            else:
                return list(kwargs.values())[0]

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

        return processed_args

    def _process_node_call_args(
        self, args: list[Any], kwargs: dict[str, Any]
    ) -> dict[str, Any]:
        path_placeholders = re.findall(r"\{([^{}]+)?\}", self.action.path)

        args_in_path = 0
        path_args = []
        path_kwargs = {}
        if len(path_placeholders) > 0:
            for placeholder in path_placeholders:
                if (placeholder != "") and (placeholder in kwargs.keys()):
                    path_kwargs[placeholder] = kwargs.pop(placeholder)
                else:
                    if len(args) <= args_in_path:
                        raise ValidationError(
                            "Number of given arguments can't be smaller than "
                            "number of path placeholders"
                        )

                    if placeholder == "":
                        path_args.append(args[args_in_path])
                    else:
                        path_kwargs[placeholder] = args[args_in_path]

                    args_in_path += 1

        return {
            "path": self.action.path.format(*path_args, **path_kwargs),
            "params": self._validate_and_map(
                self.action.params, args[args_in_path:], kwargs
            )
            if self.action.params
            else {},
            "data": self._validate_and_map(
                self.action.data, args[args_in_path:], kwargs
            )
            if self.action.data
            else {},
        }
