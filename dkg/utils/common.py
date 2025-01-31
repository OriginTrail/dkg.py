from eth_account.messages import encode_defunct
from eth_account import Account
from hexbytes import HexBytes


def get_operation_status_dict(operation_result, operation_id):
    # Check if data exists and has errorType
    operation_data = (
        {"status": operation_result.get("status"), **operation_result.get("data")}
        if operation_result.get("data")
        and operation_result.get("data", {}).get("errorType")
        else {"status": operation_result.get("status")}
    )

    return {"operationId": operation_id, **operation_data}


def get_message_signer_address(dataset_root: str, signature: dict):
    message = encode_defunct(HexBytes(dataset_root))
    r, s, v = signature.get("r"), signature.get("s"), signature.get("v")
    r = r[2:] if r.startswith("0x") else r
    s = s[2:] if s.startswith("0x") else s

    sig = "0x" + r + s + hex(v)[2:].zfill(2)

    return Account.recover_message(message, signature=sig)


def snake_to_camel(string: str) -> str:
    splitted_string = string.split("_")
    return splitted_string[0] + "".join(
        token.capitalize() for token in splitted_string[1:]
    )
