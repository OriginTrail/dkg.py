from typing import Any, Sequence, Callable
from dkg.exceptions import ValidationError
from dkg.manager import DefaultRequestManager
from dkg.method import Method
from dkg.types import TReturn
from dataclasses import replace


class Module:
    manager: DefaultRequestManager

    def retrieve_caller_fn(
        self, method: Method[Callable[..., TReturn]]
    ) -> Callable[..., TReturn]:
        def caller(*args: Any, **kwargs: Any) -> TReturn:
            processed_args = method.process_args(*args, **kwargs)
            request_params = replace(method.action, **processed_args)
            return self.manager.blocking_request(request_params)
        return caller

    def _attach_modules(self, module_definitions: dict[str, Any]) -> None:
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
