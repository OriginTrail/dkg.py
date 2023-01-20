from typing import Any, Sequence, Callable
from dkg.exceptions import ValidationError
from dkg.manager import DefaultRequestManager
from dkg.method import Method
from dkg.types import TReturn
import inspect
from io import UnsupportedOperation


class Module:
    manager: DefaultRequestManager

    def retrieve_caller_fn(
        self, method: Method[Callable[..., TReturn]]
    ) -> Callable[..., TReturn]:
        def caller(*args: Any, **kwargs: Any) -> TReturn:
            return self.manager.blocking_request(method.endpoint, *args, **kwargs)
        return caller

    def _attach_modules(
        self, module_definitions: dict[str, Any], manager: DefaultRequestManager | None = None
    ) -> None:
        for module_name, module_info in module_definitions.items():
            module_info_is_list_like = isinstance(module_info, Sequence)

            module_class = module_info[0] if module_info_is_list_like else module_info

            if hasattr(self, module_name):
                raise AttributeError(
                    f"Cannot set {self} module named '{module_name}'. "
                    " The dkg object already has an attribute with that name"
                )

            module_uses_manager = self._pass_manager(module_class)
            if module_uses_manager:
                setattr(self, module_name, module_class(manager))
            else:
                setattr(self, module_name, module_class())

            if module_info_is_list_like:
                if len(module_info) == 2:
                    submodule_definitions = module_info[1]
                    module: "Module" = getattr(self, module_name)
                    module._attach_modules(submodule_definitions)
                elif len(module_info) != 1:
                    raise ValidationError(
                        "Module definitions can only have 1 or 2 elements."
                    )

    def _pass_manager(self, module_class: Any) -> bool:
        init_params_raw = list(inspect.signature(module_class.__init__).parameters)
        module_init_params = [
            param for param in init_params_raw if param not in ["self", "args", "kwargs"]
        ]

        match len(module_init_params):
            case 0:
                return False
            case 1:
                return True
            case _:
                raise UnsupportedOperation(
                    "A module class may accept a single `DKG` instance as the first "
                    "argument of its __init__() method. More than one argument found for "
                    f"{module_class.__name__}: {module_init_params}"
                )
