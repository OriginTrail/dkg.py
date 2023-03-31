from dataclasses import asdict
from typing import Any, Callable, Sequence

from dkg.exceptions import ValidationError
from dkg.manager import DefaultRequestManager
from dkg.method import Method
from dkg.types import TReturn


class Module:
    """
    The Module class represents a collection of methods that belong to a specific module.
    It allows for the organization and management of these methods. The methods are generally
    instances of the Method class and are connected to the DefaultRequestManager to handle the
    execution of requests.

    Attributes:
        manager (DefaultRequestManager): The request manager responsible for executing
        requests in the associated methods.
    """

    manager: DefaultRequestManager

    def retrieve_caller_fn(
        self, method: Method[Callable[..., TReturn]]
    ) -> Callable[..., TReturn]:
        """
        Returns a callable function that processes the provided arguments and executes
        the associated request using the DefaultRequestManager.

        Args:
            method (Method): An instance of the Method class representing the action to
            be executed.

        Returns:
            Callable[..., TReturn]: A callable function that accepts any number of positional
            and keyword arguments, processes them according to the associated action, and
            returns the result of executing the request through the DefaultRequestManager.
        """

        def caller(*args: Any, **kwargs: Any) -> TReturn:
            processed_args = method.process_args(*args, **kwargs)
            request_params = asdict(method.action)
            request_params.update(processed_args)
            return self.manager.blocking_request(type(method.action), request_params)

        return caller

    def _attach_modules(self, module_definitions: dict[str, Any]) -> None:
        """
        Attaches the provided modules to the current instance, making them accessible as
        attributes. This function can also recursively attach submodules if they are provided
        in the module_definitions.

        Args:
            module_definitions (dict[str, Any]): A dictionary where keys are the module names
            and values are either instances of the Module class or a tuple containing the Module
            instance followed by a dictionary of submodule definitions.

        Raises:
            AttributeError: If the attribute name of a module conflicts with an existing
            attribute of the current instance.
            ValidationError: If the length of the module definition tuple is not 1 or 2.
        """
        for module_name, module_info in module_definitions.items():
            module_info_is_list_like = isinstance(module_info, Sequence)

            module = module_info[0] if module_info_is_list_like else module_info

            if hasattr(self, module_name):
                raise AttributeError(
                    f"Cannot set {self} module named '{module_name}'. "
                    " The dkg object already has an attribute with that name"
                )

            setattr(self, module_name, module)

            if module_info_is_list_like:
                if len(module_info) == 2:
                    submodule_definitions = module_info[1]
                    module: "Module" = getattr(self, module_name)
                    module._attach_modules(submodule_definitions)
                elif len(module_info) != 1:
                    raise ValidationError(
                        "Module definitions can only have 1 or 2 elements."
                    )
