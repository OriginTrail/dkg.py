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

import hashlib
import json

from dkg.types import Address, NQuads
from eth_abi.packed import encode_packed


def generate_assertion_metadata(assertion: NQuads) -> dict[str, int]:
    return {
        "size": len(json.dumps(assertion, separators=(",", ":")).encode("utf-8")),
        "triples_number": len(assertion),
        "chunks_number": len(assertion),  # TODO: Change when chunking introduced
    }


def generate_keyword(contract_address: Address, assertion_id: bytes) -> bytes:
    return encode_packed(
        ["address", "bytes32"],
        [contract_address, assertion_id],
    )


def generate_agreement_id(
    contract_address: Address,
    token_id: int,
    keyword: bytes,
) -> bytes:
    return hashlib.sha256(
        encode_packed(
            ["address", "uint256", "bytes"],
            [contract_address, token_id, keyword],
        )
    ).digest()
