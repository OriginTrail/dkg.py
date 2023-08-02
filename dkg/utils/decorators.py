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
