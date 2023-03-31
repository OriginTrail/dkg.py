from dkg.exceptions import ValidationError
from dkg.types import UAL, Address, ChecksumAddress


def format_ual(
    blockchain: str, contract_address: Address | ChecksumAddress, token_id: int
) -> UAL:
    """
    Formats a Universal Asset Locator (UAL) string using the provided blockchain, contract
    address, and token ID.

    Args:
        blockchain (str): The blockchain identifier, such as 'ethereum'.
        contract_address (Address | ChecksumAddress): The contract address associated with
        the asset.
        token_id (int): The unique identifier for the specific asset within the contract.

    Returns:
        UAL: The formatted Universal Asset Locator string.
    """
    return f"did:dkg:{blockchain.lower()}/{contract_address.lower()}/{token_id}"


def parse_ual(ual: UAL) -> dict[str, str | Address | int]:
    """
    Parses a Universal Asset Locator (UAL) string and returns a dictionary containing the
    extracted blockchain,
    contract address, and token ID.

    Args:
        ual (UAL): The Universal Asset Locator string to be parsed.

    Returns:
        dict[str, str | Address | int]: A dictionary containing the extracted 'blockchain',
        'contractAddress', and 'tokenId' from the given UAL string.

    Raises:
        ValidationError: If the provided UAL string is invalid.
    """
    args = ual.split(":")[-1].split("/")

    if len(args) != 3:
        raise ValidationError("Invalid UAL!")

    blockchain, contract_address, token_id = args

    return {
        "blockchain": blockchain,
        "contractAddress": Address(contract_address),
        "tokenId": int(token_id),
    }
