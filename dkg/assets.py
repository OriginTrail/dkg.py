from dkg.module import Module
from dkg.method import Method
from dkg.dataclasses import NodeResponseDict
from dkg.types import UAL, Address, JSONLD, HexStr
from dkg._utils.node_request import NodeRequest, GetOperationStatus
from dkg._utils.blockchain_request import BlockchainRequest
from dkg.manager import DefaultRequestManager
from dkg._utils.ual import parse_ual
from dkg._utils.decorators import retry
from dkg.exceptions import OperationNotFinished, OperationFailed
from web3 import Web3
from pyld import jsonld


class ContentAsset(Module):
    def __init__(self, manager: DefaultRequestManager):
        self.manager = manager

    _local_store = Method(NodeRequest.local_store)

    _increase_allowance = Method(BlockchainRequest.increase_allowance)
    _decrease_allowance = Method(BlockchainRequest.decrease_allowance)
    _create = Method(BlockchainRequest.create_asset)
    _publish = Method(NodeRequest.publish)

    def create(self):
        pass

    _get = Method(NodeRequest.get)
    _get_operation_result = Method(NodeRequest.get_operation_result)
    _get_latest_assertion_id = Method(BlockchainRequest.get_latest_assertion_id)

    def get(
        self, ual: UAL, validate: bool = False
    ) -> dict[str, HexStr | list[JSONLD] | dict[str, str]]:
        operation_id: NodeResponseDict = self._get(ual, hashFunctionId=1)['operationId']

        @retry(catch=OperationNotFinished, max_retries=5, base_delay=1, backoff=2)
        def get_operation_result() -> NodeResponseDict:
            operation_result = self._get_operation_result(
                operation='get',
                operation_id=operation_id,
            )

            match GetOperationStatus(operation_result['status']):
                case GetOperationStatus.COMPLETED:
                    return operation_result
                case GetOperationStatus.FAILED:
                    raise OperationFailed(
                        f"Operation failed! {operation_result['data']['errorType']}: "
                        f"{operation_result['data']['errorMessage']}."
                    )
                case _:
                    raise OperationNotFinished("Operation isn't finished")

        operation_result = get_operation_result()
        assertion = operation_result['data']['assertion']

        token_id = parse_ual(ual)['tokenId']
        latest_assertion_id = self._get_latest_assertion_id(token_id)

        if validate:
            pass

        assertion_json_ld: list[JSONLD] = jsonld.from_rdf(
            '\n'.join(assertion),
            {'algorithm': 'URDNA2015', 'format': 'application/n-quads'}
        )

        return {
            'assertionId': Web3.to_hex(latest_assertion_id),
            'assertion': assertion_json_ld,
            'operation': {
                'operation_id': operation_id,
                'status': operation_result['status'],
            },
        }

    _owner = Method(BlockchainRequest.owner_of)

    def owner(self, token_id: int) -> Address:
        return self._owner(token_id)


class Assets(Module):
    ContentAsset: ContentAsset
