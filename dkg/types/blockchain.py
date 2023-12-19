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

from typing import Literal, NamedTuple, TypedDict


class ABIParameter(TypedDict, total=False):
    name: str
    type: str
    indexed: bool | None  # Only used in event inputs
    components: list["ABIParameter"] | None  # Used for tuple types


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


Environment = Literal["development", "devnet", "testnet", "mainnet"]


class AgreementData(NamedTuple):
    startTime: int
    epochsNumber: int
    epochLength: int
    tokens: list[int]
    scoreFunctionIdAndProofWindowOffsetPerc: list[int]
