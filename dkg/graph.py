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

from rdflib.plugins.sparql.parser import parseQuery

from dkg.dataclasses import NodeResponseDict
from dkg.exceptions import OperationNotFinished
from dkg.manager import DefaultRequestManager
from dkg.method import Method
from dkg.module import Module
from dkg.types import NQuads
from dkg.utils.decorators import retry
from dkg.utils.node_request import NodeRequest, validate_operation_status
from dkg.services.input_service import InputService
from dkg.constants import Operations
from utils.finality import finality_status, finality

class Graph(Module):
    def __init__(self, manager: DefaultRequestManager, input_service: InputService):
        self.manager = manager
        self.input_service = input_service

    _query = Method(NodeRequest.query)
    _get_operation_result = Method(NodeRequest.get_operation_result)

    def query(
        self,
        query: str,
        options: dict = {},
    ) -> NQuads:
        arguments = self.input_service.get_query_arguments(options)

        max_number_of_retries = arguments.get("max_number_of_retries")
        frequency = arguments.get("frequency")
        paranet_ual = arguments.get("paranet_ual")
        repository = arguments.get("repository")

        parsed_query = parseQuery(query)
        query_type = parsed_query[1].name.replace("Query", "").upper()

        operation_id: NodeResponseDict = self._query(
            query, query_type, repository, paranet_ual
        )["operationId"]
        operation_result = self.get_operation_result(
            operation_id, Operations.QUERY.value, max_number_of_retries, frequency
        )

        return operation_result["data"]

    @retry(catch=OperationNotFinished, max_retries=5, base_delay=1, backoff=2)
    def get_operation_result(
        self, operation_id: str, operation: str, max_retries: int, frequency: int
    ):
        @retry(
            catch=OperationNotFinished,
            max_retries=max_retries,
            base_delay=frequency,
            backoff=2,
        )

        def retry_get_operation_result():
            operation_result = self._get_operation_result(
                operation_id=operation_id,
                operation=operation,
            )
            validate_operation_status(operation_result)

            return operation_result

        return retry_get_operation_result()

    def publish_finality(self, UAL, options=None):
        if options is None:
            options = {}

        blockchain = self.manager.blockchain_provider.blockchain_id
        max_number_of_retries, frequency, minimum_number_of_finalization_confirmations = self.input_service.get_publish_finality_arguments(options)
        #auth_token = self.manager.node_provider.auth_token
        #endpoint = self.manager.node_provider.endpoint_uri

        #Probably needs some validation but its not implemented

        try:
            finality_status_result = finality_status(UAL, minimum_number_of_finalization_confirmations, max_number_of_retries, frequency)
        except Exception as e:
            return {"status": "ERROR", "error": str(e)}

        if finality_status_result == 0:
            try:
                finality_operation_id = finality(UAL, minimum_number_of_finalization_confirmations, max_number_of_retries, frequency)
            except Exception as e:
                return {"status": "ERROR", "error": str(e)}
            
            try:
                return self.get_operation_result(finality_operation_id, 'finality', max_number_of_retries, frequency)
            except Exception as e:
                return {"status": "NOT FINALIZED", "error": str(e)}


        elif finality_status_result >= minimum_number_of_finalization_confirmations:
            return {
                "status": "FINALIZED",
                "numberOfConfirmations": finality_status_result,
                "requiredConfirmations": minimum_number_of_finalization_confirmations
            }
        else:
            return {
                "status": "NOT FINALIZED",
                "numberOfConfirmations": finality_status_result,
                "requiredConfirmations": minimum_number_of_finalization_confirmations
            }

