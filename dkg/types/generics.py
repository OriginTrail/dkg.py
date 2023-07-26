from typing import Any, Callable, TypeVar

TFunc = TypeVar("TFunc", bound=Callable[..., Any])
TReturn = TypeVar("TReturn")
