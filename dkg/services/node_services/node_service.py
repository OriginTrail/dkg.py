from dkg.managers.manager import DefaultRequestManager
from dkg.method import Method
from dkg.modules.module import Module
import time
from dkg.utils.decorators import retry
from dkg.exceptions import (
    OperationNotFinished,
)
from dkg.request_managers.node_request import (
    NodeRequest,
    validate_operation_status,
)


class NodeService(Module):
    def __init__(self, manager: DefaultRequestManager):
        self.manager = manager

    _get_operation_result = Method(NodeRequest.get_operation_result)
    _finality_status = Method(NodeRequest.finality_status)
    _ask = Method(NodeRequest.ask)
    _publish = Method(NodeRequest.publish)
    _get = Method(NodeRequest.get)
    _query = Method(NodeRequest.query)

    def get_operation_result(
        self, operation_id: str, operation: str, max_retries: int, frequency: int
    ):
        @retry(
            catch=OperationNotFinished,
            max_retries=max_retries,
            base_delay=frequency,
            backoff=1,
        )
        def retry_get_operation_result():
            operation_result = self._get_operation_result(
                operation_id=operation_id,
                operation=operation,
            )
            validate_operation_status(operation_result)

            return operation_result

        return retry_get_operation_result()

    def finality_status(
        self,
        ual: str,
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

            if retries > 0:
                time.sleep(frequency)

            retries += 1

            try:
                try:
                    response = self._finality_status(ual=ual)
                except Exception as e:
                    response = None
                    print(f"failed: {e}")

                if response is not None:
                    finality = response.get("finality", 0)
                    if finality >= required_confirmations:
                        break

            except Exception:
                finality = 0

        return finality

    def ask(self, ual, required_confirmations, max_number_of_retries, frequency):
        confirmations_count = 0
        retries = 0

        while (
            confirmations_count < required_confirmations
            and retries < max_number_of_retries
        ):
            if retries > max_number_of_retries:
                raise Exception(
                    f"Unable to achieve required confirmations. "
                    f"Max number of retries ({max_number_of_retries}) reached."
                )

            if retries > 0:
                time.sleep(frequency)

            retries += 1

            try:
                try:
                    response = self._ask(
                        ual=ual, minimumNumberOfNodeReplications=required_confirmations
                    )
                except Exception as e:
                    response = None
                    print(f"failed: {e}")

                if response is not None:
                    number_of_confirmations = response.json().get(
                        "numberOfConfirmations", 0
                    )
                    if number_of_confirmations >= required_confirmations:
                        confirmations_count = number_of_confirmations

            except Exception as e:
                confirmations_count = 0
                print(f"Retry {retries + 1}/{max_number_of_retries} failed: {e}")

            return confirmations_count

    def publish(
        self,
        dataset_root,
        dataset,
        blockchain_id,
        hash_function_id,
        minimum_number_of_node_replications,
    ):
        return self._publish(
            dataset_root,
            dataset,
            blockchain_id,
            hash_function_id,
            minimum_number_of_node_replications,
        )

    def get(
        self,
        ual_with_state,
        content_type,
        include_metadata,
        hash_function_id,
        paranet_ual,
        subject_ual,
    ):
        return self._get(
            ual_with_state,
            content_type,
            include_metadata,
            hash_function_id,
            paranet_ual,
            subject_ual,
        )

    def query(
        self,
        query,
        query_type,
        repository,
        paranet_ual,
    ):
        return self._query(query, query_type, repository, paranet_ual)
