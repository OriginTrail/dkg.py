from dkg.managers.async_manager import AsyncRequestManager
from dkg.method import Method
from dkg.constants import OperationStatuses, ErrorType, Status
from dkg.request_managers.node_request import NodeRequest
from dkg.modules.async_module import AsyncModule
from typing import Dict, Any
from dkg.types import UAL
from dkg.dataclasses import NodeResponseDict
import asyncio


class AsyncNodeService(AsyncModule):
    def __init__(self, manager: AsyncRequestManager):
        self.manager = manager

    _info = Method(NodeRequest.info)
    _get_operation_result = Method(NodeRequest.get_operation_result)
    _finality_status = Method(NodeRequest.finality_status)
    _ask = Method(NodeRequest.ask)
    _publish = Method(NodeRequest.publish)
    _get = Method(NodeRequest.get)
    _query = Method(NodeRequest.query)

    async def info(self) -> NodeResponseDict:
        return await self._info()

    async def get_operation_result(
        self,
        operation_id: str,
        operation: str,
        max_retries: int,
        frequency: int,
    ) -> Dict[str, Any]:
        response = {"status": OperationStatuses.PENDING.value}

        retries = 0

        while True:
            if retries > max_retries:
                response["data"] = {
                    "errorType": ErrorType.DKG_CLIENT_ERROR.value,
                    "errorMessage": "Unable to get results. Max number of retries reached.",
                }
                break

            if retries > 0:
                await asyncio.sleep(frequency)

            retries += 1

            try:
                result = await self._get_operation_result(
                    operation=operation,
                    operation_id=operation_id,
                )
                response = {"data": result}
            except Exception:
                response = {"data": {"status": Status.NETWORK_ERROR.value}}

            # Check completion conditions
            if (
                response["data"].get("status") == OperationStatuses.COMPLETED.value
                or response["data"].get("status") == OperationStatuses.FAILED.value
            ):
                break

        return response["data"]

    async def finality_status(
        self,
        ual: UAL,
        required_confirmations: int,
        max_number_of_retries: int,
        frequency: int,
    ):
        retries = 0
        finality = 0

        while finality < required_confirmations and retries <= max_number_of_retries:
            if retries > max_number_of_retries:
                raise Exception(
                    f"Unable to achieve required confirmations. "
                    f"Max number of retries ({max_number_of_retries}) reached."
                )

            # Sleep between attempts (except for first try)
            if retries > 0:
                await asyncio.sleep(frequency)

            retries += 1

            try:
                response = await self._finality_status(ual)
                finality = response.get("finality", 0)
            except Exception:
                finality = 0

        return finality

    async def ask(
        self,
        ual: UAL,
        required_confirmations: int,
        max_number_of_retries: int,
        frequency: int,
    ):
        finality_id = 0
        retries = 0

        while finality_id < required_confirmations and retries < max_number_of_retries:
            if retries > max_number_of_retries:
                raise Exception(
                    f"Unable to achieve required confirmations. "
                    f"Max number of retries ({max_number_of_retries}) reached."
                )

            if retries > 0:
                await asyncio.sleep(frequency)

            retries += 1

            try:
                try:
                    response = await self._ask(
                        ual=ual, minimumNumberOfNodeReplications=required_confirmations
                    )
                except Exception as e:
                    response = None
                    print(f"failed: {e}")

                if response is not None:
                    operation_id = response.json().get("operationId", 0)
                    if operation_id >= required_confirmations:
                        finality_id = operation_id

            except Exception as e:
                finality_id = 0
                print(f"Retry {retries + 1}/{max_number_of_retries} failed: {e}")

            return finality_id

    async def publish(
        self,
        dataset_root,
        dataset,
        blockchain_id,
        hash_function_id,
        minimum_number_of_node_replications,
    ):
        return await self._publish(
            dataset_root,
            dataset,
            blockchain_id,
            hash_function_id,
            minimum_number_of_node_replications,
        )

    async def get(
        self,
        ual_with_state,
        content_type,
        include_metadata,
        hash_function_id,
        paranet_ual,
        subject_ual,
    ):
        return await self._get(
            ual_with_state,
            content_type,
            include_metadata,
            hash_function_id,
            paranet_ual,
            subject_ual,
        )

    async def query(
        self,
        query,
        query_type,
        repository,
        paranet_ual,
    ):
        return await self._query(query, query_type, repository, paranet_ual)
