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


class NodeHTTPProvider:
    def __init__(self, endpoint_uri: URI | str):
        self.endpoint_uri = URI(endpoint_uri)

    def make_request(
        self,
        method: HTTPRequestMethod,
        path: str,
        params: dict[str, Any] = {},
        data: dict[str, Any] = {},
    ) -> Response:
        request_func = getattr(self, method.name.lower())

        match method:
            case HTTPRequestMethod.GET:
                return request_func(path, params)
            case HTTPRequestMethod.POST:
                return request_func(path, data)
            case HTTPRequestMethod():
                raise HTTPRequestMethodNotSupported(
                    f"{method.name} method isn't supported"
                )

    def get(self, path: str, params: dict[str, Any] = {}) -> NodeResponseDict:
        try:
            response = requests.get(f"{self.endpoint_uri}/{path}", params=params)
            return NodeResponseDict(response.json())
        except requests.exceptions.HTTPError as err:
            raise NodeRequestError(err)

    def post(self, path: str, data: dict[str, Any] = {}) -> NodeResponseDict:
        try:
            response = requests.post(f"{self.endpoint_uri}/{path}", json=data)
            return NodeResponseDict(response.json())
        except requests.exceptions.HTTPError as err:
            raise NodeRequestError(err)
