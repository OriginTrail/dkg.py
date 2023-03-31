import itertools
import re
from typing import TYPE_CHECKING, Any, Generic, Type

from dkg.exceptions import ValidationError
from dkg.types import TFunc
from dkg.utils.blockchain_request import ContractInteraction, ContractTransaction
from dkg.utils.node_request import NodeCall
from dkg.utils.string_transformations import snake_to_camel

if TYPE_CHECKING:
    from dkg.module import Module


class Method(Generic[TFunc]):
    """
    A generic class representing a method for handling ContractInteraction and NodeCall actions.

    Attributes:
        action (ContractInteraction | NodeCall): The action to be performed by the method.
    """

    def __init__(self, action: ContractInteraction | NodeCall):
        """
        Initializes a Method object with the given action.

        Args:
            action (ContractInteraction | NodeCall): The action to be performed by the method.
        """
        self.action = action

    def __get__(
        self, obj: "Module | None" = None, _: Type["Module"] | None = None
    ) -> TFunc:
        """
        Retrieves the function associated with the Method object.

        Args:
            obj (Module | None): The module instance, usually attached to a dkg instance.
            _ (Type['Module'] | None): Ignored parameter.

        Returns:
            TFunc: The function associated with the Method object.

        Raises:
            TypeError: If the method is called directly without a module instance.
        """
        if obj is None:
            raise TypeError(
                "Direct calls to methods are not supported. "
                "Methods must be called from a module instance, "
                "usually attached to a dkg instance."
            )
        return obj.retrieve_caller_fn(self)

    def process_args(self, *args: Any, **kwargs: Any):
        """
        Processes the arguments for the action based on the action type.

        Args:
            *args (Any): Positional arguments.
            **kwargs (Any): Keyword arguments.

        Returns:
            dict: A dictionary containing processed arguments.
        """
        match self.action:
            case ContractInteraction():
                return {
                    "args": self._validate_and_map(self.action.args, args, kwargs),
                    "state_changing": isinstance(self.action, ContractTransaction),
                }
            case NodeCall():
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
                    "params": (
                        self._validate_and_map(
                            self.action.params, args[args_in_path:], kwargs
                        )
                        if self.action.params
                        else {}
                    ),
                    "data": (
                        self._validate_and_map(
                            self.action.data, args[args_in_path:], kwargs
                        )
                        if self.action.data
                        else {}
                    ),
                }

            case _:
                return {}

    def _validate_and_map(
        self,
        required_args: dict[str, Type] | Type,
        args: list[Any],
        kwargs: dict[str, Any],
    ) -> dict[str, Any]:
        """
        Validates and maps the provided arguments based on the required arguments.

        Args:
            required_args (dict[str, Type] | Type): The required arguments for the action.
            args (list[Any]): The positional arguments provided.
            kwargs (dict[str, Any]): The keyword arguments provided.

        Returns:
            dict[str, Any]: A dictionary containing the validated and mapped arguments.

        Raises:
            ValidationError: If the provided arguments do not meet the requirements.
        """
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
