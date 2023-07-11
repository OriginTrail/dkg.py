from dkg.exceptions import ValidationError
from dkg.types import UAL, Address, ChecksumAddress
from web3 import Web3


def format_ual(
    blockchain: str, contract_address: Address | ChecksumAddress, token_id: int
) -> UAL:
    return f"did:dkg:{blockchain.lower()}/{contract_address.lower()}/{token_id}"


def parse_ual(ual: UAL) -> dict[str, str | Address | int]:
    args = ual.split(":")[-1].split("/")

    if len(args) != 3:
        raise ValidationError("Invalid UAL!")

    blockchain, contract_address, token_id = args

    return {
        "blockchain": blockchain,
        "contract_address": Web3.to_checksum_address(contract_address),
        "token_id": int(token_id),
    }
