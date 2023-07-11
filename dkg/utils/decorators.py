import time
from functools import wraps
from typing import Any, Callable

from dkg.exceptions import NodeRequestError


def retry(
    catch: Exception, max_retries: int, base_delay: int, backoff: float
) -> Callable[[Callable], Callable]:
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            _delay = base_delay

            for _ in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except catch:
                    time.sleep(_delay)
                    _delay *= backoff

            raise NodeRequestError(
                f"Failed executing {func.__name__} after {max_retries} retries."
            )

        return wrapper

    return decorator
