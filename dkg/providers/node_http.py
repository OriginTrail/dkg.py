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
