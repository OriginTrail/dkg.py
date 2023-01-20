from dkg.types import URI
from dkg.exceptions import NodeRequestError
import requests
from requests import Response
from typing import Any


class NodeHTTPProvider:
    def __init__(self, endpoint_uri: URI | str):
        self.endpoint_uri = URI(endpoint_uri)

    def make_request(self, method: str, path: str, data: Any = None) -> Response:
        request_func = getattr(self, method)
        return request_func(path) if method == 'get' else request_func(path, data)

    def get(self, path: str) -> Response:
        try:
            response = requests.get(f"{self.endpoint_uri}/{path}")
            return response.json()
        except requests.exceptions.HTTPError as err:
            raise NodeRequestError(err)

    def post(self, path: str, data: Any) -> Response:
        try:
            response = requests.post(f"{self.endpoint_uri}/{path}", json=data)
            return response.json()
        except requests.exceptions.HTTPError as err:
            raise NodeRequestError(err)
