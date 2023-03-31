from typing import Literal

from pyld import jsonld
from rdflib.plugins.sparql.parser import parseQuery

from dkg.dataclasses import NodeResponseDict
from dkg.exceptions import DatasetOutputFormatNotSupported, OperationNotFinished
from dkg.manager import DefaultRequestManager
from dkg.method import Method
from dkg.module import Module
from dkg.types import JSONLD, NQuads
from dkg.utils.decorators import retry
from dkg.utils.node_request import NodeRequest, validate_operation_status
from dkg.utils.rdf import normalize_dataset


class Graph(Module):
    """
    A class to represent the Graph component in the Decentralized Knowledge Graph (DKG)
    system.
    This class inherits from the Module class and provides methods for querying and managing
    the graph.

    Attributes:
        manager (DefaultRequestManager): An instance of DefaultRequestManager for managing
        requests to the graph.
    """

    def __init__(self, manager: DefaultRequestManager):
        """
        Initializes a Graph object with the given request manager.

        Args:
            manager (DefaultRequestManager): An instance of DefaultRequestManager for managing
            requests to the graph.
        """
        self.manager = manager

    _query = Method(NodeRequest.query)
    _get_operation_result = Method(NodeRequest.get_operation_result)

    def query(
        self,
        query: str,
        repository: str,
        output_format: Literal["JSON-LD", "N-Quads"] = "JSON-LD",
    ) -> JSONLD | NQuads:
        """
        Executes a SPARQL query on the graph and returns the results in the specified output
        format.

        Args:
            query (str): The SPARQL query to be executed.
            repository (str): The repository to query.
            output_format (Literal['JSON-LD', 'N-Quads']): The desired output format for
            the query results. Default is 'JSON-LD'.

        Returns:
            JSONLD | NQuads: The query results in the specified output format.

        Raises:
            DatasetOutputFormatNotSupported: If the output format is not supported.
        """
        parsed_query = parseQuery(query)
        query_type = parsed_query[1].name.replace("Query", "").upper()

        operation_id: NodeResponseDict = self._query(query, query_type, repository)[
            "operationId"
        ]
        operation_result = self.get_operation_result(operation_id, "query")

        match output_format.lower():
            case "json-ld" | "jsonld":
                return jsonld.from_rdf(operation_result["data"])
            case "n-quads" | "nquads":
                return normalize_dataset(operation_result["data"], "N-Quads")
            case _:
                raise DatasetOutputFormatNotSupported(
                    f"Dataset input format isn't supported: {output_format}. "
                    "Supported formats: JSON-LD / N-Quads."
                )

    _get_operation_result = Method(NodeRequest.get_operation_result)

    @retry(catch=OperationNotFinished, max_retries=5, base_delay=1, backoff=2)
    def get_operation_result(
        self, operation_id: str, operation: str
    ) -> NodeResponseDict:
        """
        Retrieves the result of a previously executed operation on the graph, retrying up
        to 5 times with exponential backoff if the operation is not yet finished.

        Args:
            operation_id (str): The identifier of the operation.
            operation (str): The type of operation.

        Returns:
            NodeResponseDict: A dictionary containing the operation result.

        Raises:
            OperationNotFinished: If the operation is not finished after the maximum number
            of retries.
        """
        operation_result = self._get_operation_result(
            operation_id=operation_id,
            operation=operation,
        )

        validate_operation_status(operation_result)

        return operation_result
