from types import MappingProxyType
from typing import Any

import requests
from requests import Response

from dkg.dataclasses import HTTPRequestMethod, NodeResponseDict
from dkg.exceptions import HTTPRequestMethodNotSupported, NodeRequestError
from dkg.types import URI


class NodeHTTPProvider:
    """
    A class for making HTTP requests to a node.

    Attributes:
        endpoint_uri (URI): The URI of the endpoint to send requests to.
    """

    def __init__(self, endpoint_uri: URI | str):
        """
        Initialize a NodeHTTPProvider instance with the specified endpoint URI.

        Args:
            endpoint_uri (URI | str): The URI of the endpoint to send requests to.
        """
        self.endpoint_uri = URI(endpoint_uri)

    def make_request(
        self,
        method: HTTPRequestMethod,
        path: str,
        params: dict[str, Any] | MappingProxyType = MappingProxyType({}),
        data: dict[str, Any] | MappingProxyType = MappingProxyType({}),
    ) -> Response:
        """
        Make an HTTP request to the node using the specified method, path, and
        parameters.

        Args:
            method (HTTPRequestMethod): The HTTP request method to use (GET or POST).
            path (str): The path for the request.
            params (dict[str, Any], optional): The query parameters for the request.
            Defaults to an empty dictionary.
            data (dict[str, Any], optional): The JSON data for the request. Defaults to
            an empty dictionary.

        Returns:
            Response: The response object returned by the node.

        Raises:
            HTTPRequestMethodNotSupported: If the specified method is not supported.
        """
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

    def get(
        self, path: str, params: dict[str, Any] | MappingProxyType = MappingProxyType({}),
    ) -> NodeResponseDict:
        """
        Make an HTTP GET request to the node using the specified path and query
        parameters.

        Args:
            path (str): The path for the request.
            params (dict[str, Any], optional): The query parameters for the request.
            Defaults to an empty dictionary.

        Returns:
            NodeResponseDict: A dictionary-like object containing the JSON response
            from the node.

        Raises:
            NodeRequestError: If the request encounters an error.
        """
        try:
            response = requests.get(f"{self.endpoint_uri}/{path}", params=params)
            return NodeResponseDict(response.json())
        except requests.exceptions.HTTPError as err:
            raise NodeRequestError(err)

    def post(
        self, path: str, data: dict[str, Any] | MappingProxyType = MappingProxyType({}),
    ) -> NodeResponseDict:
        """
        Make an HTTP POST request to the node using the specified path and JSON data.

        Args:
            path (str): The path for the request.
            data (dict[str, Any], optional): The JSON data for the request. Defaults to
            an empty dictionary.

        Returns:
            NodeResponseDict: A dictionary-like object containing the JSON response
            from the node.

        Raises:
            NodeRequestError: If the request encounters an error.
        """
        try:
            response = requests.post(f"{self.endpoint_uri}/{path}", json=data)
            return NodeResponseDict(response.json())
        except requests.exceptions.HTTPError as err:
            raise NodeRequestError(err)
