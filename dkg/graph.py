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

from typing import Literal, Type

from pyld import jsonld
from rdflib.plugins.sparql.parser import parseQuery

from dkg.dataclasses import NodeResponseDict, KnowledgeAssetContentVisibility
from dkg.exceptions import (
    OperationNotFinished, 
    MissingKnowledgeAssetState,
    InvalidKnowledgeAsset,
    DatasetOutputFormatNotSupported,
)
from dkg.manager import DefaultRequestManager
from dkg.method import Method
from dkg.module import Module
from dkg.types import NQuads, JSONLD
from dkg.utils.decorators import retry
from dkg.utils.node_request import NodeRequest, validate_operation_status


class Graph(Module):
    def __init__(self, manager: DefaultRequestManager):
        self.manager = manager

    _get = Method(NodeRequest.get)

    def get(
        self,
        ual: UAL,
        state: int = 0,
        content_visibility: str = KnowledgeAssetContentVisibility.ALL,
        output_format: Literal["JSON-LD", "N-Quads"] = "JSON-LD",
        validate: bool = True,
        include_metadata: bool = False,
        paranetUAL = None,
    ) -> dict[str, UAL | list[JSONLD] | dict[str, str]]:
        content_visibility = content_visibility.upper()
        output_format = output_format.upper()

        get_public_operation_id: NodeResponseDict = self._get(
            ual + ':' + state,
            content_visibility,
            paranetUAL,
            hashFunctionId=1,
            includeMetadata=include_metadata,
        )["operationId"]

        get_public_operation_result = self.get_operation_result(
            get_public_operation_id, "get"
        )

        assertion = get_public_operation_result["data"].get("assertion", None)
        if assertion is None:
            raise MissingKnowledgeAssetState("Unable to find state on the network!")

        if validate:
            isValid = True # TODO: validate assertion
            if not isValid:
                raise InvalidKnowledgeAsset("Validation failed")

        formatted_assertion = assertion
        match output_format:
            case "NQUADS" | "N-QUADS":
                formatted_assertion: list[JSONLD] = jsonld.from_rdf(
                    "\n".join(assertion),
                    {"algorithm": "URDNA2015", "format": "application/n-quads"},
                )
            case "JSONLD" | "JSON-LD":
                formatted_assertion = "\n".join(assertion)

            case _:
                raise DatasetOutputFormatNotSupported(
                    f"{output_format} isn't supported!"
                )

        result = {
            "asertion": formatted_assertion,
            "operation": {
                "get": {
                    "operationId": get_public_operation_id,
                    "status": get_public_operation_result["status"],
                },
            },
        }

        return result

    _query = Method(NodeRequest.query)

    def query(
        self,
        query: str,
        repository: str,
    ) -> NQuads:
        parsed_query = parseQuery(query)
        query_type = parsed_query[1].name.replace("Query", "").upper()

        operation_id: NodeResponseDict = self._query(query, query_type, repository)[
            "operationId"
        ]
        operation_result = self.get_operation_result(operation_id, "query")

        return operation_result["data"]

    _get_operation_result = Method(NodeRequest.get_operation_result)

    @retry(catch=OperationNotFinished, max_retries=5, base_delay=1, backoff=2)
    def get_operation_result(
        self, operation_id: str, operation: str
    ) -> NodeResponseDict:
        operation_result = self._get_operation_result(
            operation_id=operation_id,
            operation=operation,
        )

        validate_operation_status(operation_result)

        return operation_result
