from typing import TypeVar, Callable, Any

TFunc = TypeVar("TFunc", bound=Callable[..., Any])
TReturn = TypeVar("TReturn")
