from typing import TypedDict, NamedTuple


class ABIParameter(TypedDict, total=False):
    name: str
    type: str
    indexed: bool | None  # Only used in event inputs
    components: list['ABIParameter'] | None  # Used for tuple types


class ABICommon(TypedDict, total=False):
    type: str
    name: str | None
    inputs: list[ABIParameter]


class ABIFunction(ABICommon):
    outputs: list[ABIParameter]
    stateMutability: str


class ABIEvent(ABICommon):
    anonymous: bool


class ABIError(TypedDict):
    type: str
    name: str
    inputs: list[ABIParameter]


ABIElement = ABIFunction | ABIEvent | ABIError
ABI = list[ABIElement]


class AgreementData(NamedTuple):
    startTime: int
    epochsNumber: int
    epochLength: int
    tokensInfo: list[int]
    scoreFunctionIdAndProofWindowOffsetPerc: list[int]
