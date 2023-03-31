import time
from functools import wraps
from typing import Any, Callable

from dkg.exceptions import NodeRequestError


def retry(
    catch: Exception, max_retries: int, base_delay: int, backoff: float
) -> Callable[[Callable], Callable]:
    """
    A decorator that allows a function to be retried for a specified number of times if
    it raises a specified exception.

    Args:
        catch (Exception): The exception to be caught and handled by the retry mechanism.
        max_retries (int): The maximum number of retries allowed before raising a
        NodeRequestError.
        base_delay (int): The initial delay (in seconds) before retrying the function.
        backoff (float): The factor by which the delay increases after each failed attempt.

    Returns:
        Callable: A wrapped function that will be retried based on the specified parameters.

    Raises:
        NodeRequestError: If the function fails to execute successfully after max_retries
        attempts.
    """

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
