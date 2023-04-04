import json
from dkg.types import NQuads, Address
import hashlib
from eth_abi.packed import encode_packed


def generate_assertion_metadata(assertion: NQuads) -> dict[str, int]:
    return {
        "size": len(json.dumps(assertion, separators=(',', ':')).encode('utf-8')),
        "triples_number": len(assertion),
        "chunks_number": len(assertion),  # TODO: Change when chunking introduced
    }


def generate_keyword(contract_address: Address, assertion_id: bytes) -> bytes:
    return encode_packed(
        ["address", "bytes32"],
        [contract_address, assertion_id],
    )


def generate_agreement_id(
    contract_address: Address, token_id: int, keyword: bytes,
) -> bytes:
    return hashlib.sha256(
        encode_packed(
            ["address", "uint256", "bytes"],
            [contract_address, token_id, keyword],
        )
    ).digest()
