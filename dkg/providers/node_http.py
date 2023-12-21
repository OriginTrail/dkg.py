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

from typing import Any

import requests
from dkg.dataclasses import HTTPRequestMethod, NodeResponseDict
from dkg.exceptions import HTTPRequestMethodNotSupported, NodeRequestError
from dkg.types import URI
from requests import Response
from requests.exceptions import HTTPError, ConnectionError, Timeout, RequestException


class NodeHTTPProvider:
    def __init__(self, endpoint_uri: URI | str, auth_token: str | None = None):
        self.endpoint_uri = URI(endpoint_uri)
        self.auth_token = auth_token

    def make_request(
        self,
        method: HTTPRequestMethod,
        path: str,
        params: dict[str, Any] = {},
        data: dict[str, Any] = {},
    ) -> Response:
        request_func = getattr(self, method.name.lower())

        headers = self._prepare_headers()

        match method:
            case HTTPRequestMethod.GET:
                return request_func(path, params, headers)
            case HTTPRequestMethod.POST:
                return request_func(path, data, headers)
            case HTTPRequestMethod():
                raise HTTPRequestMethodNotSupported(
                    f"{method.name} method isn't supported"
                )

    def get(
        self, path: str, params: dict[str, Any] = {}, headers: dict[str, str] = {}
    ) -> NodeResponseDict:
        try:
            response = requests.get(
                f"{self.endpoint_uri}/{path}",
                params=params,
                headers=headers,
            )

            response.raise_for_status()

            try:
                return NodeResponseDict(response.json())
            except ValueError as err:
                raise NodeRequestError(f"JSON decoding failed: {err}")

        except (HTTPError, ConnectionError, Timeout, RequestException) as err:
            raise NodeRequestError(f"Request failed: {err}")

    def post(
        self, path: str, data: dict[str, Any] = {}, headers: dict[str, str] = {}
    ) -> NodeResponseDict:
        try:
            response = requests.post(
                f"{self.endpoint_uri}/{path}",
                json=data,
                headers=headers,
            )
            response.raise_for_status()

            try:
                return NodeResponseDict(response.json())
            except ValueError as err:
                raise NodeRequestError(f"JSON decoding failed: {err}")

        except (HTTPError, ConnectionError, Timeout, RequestException) as err:
            raise NodeRequestError(f"Request failed: {err}")

    def _prepare_headers(self) -> dict[str, str]:
        return self._prepare_auth_header()

    def _prepare_auth_header(self) -> dict[str, str]:
        if self.auth_token:
            return {"Authorization": f"Bearer {self.auth_token}"}
        return {}
