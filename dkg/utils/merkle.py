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

import copy
import hashlib
from typing import Callable

from dkg.exceptions import LeafNotInTree
from dkg.types import HexStr
from eth_abi.packed import encode_packed
from hexbytes import HexBytes
from web3 import Web3


def solidity_keccak256(data: HexStr) -> HexStr:
    bytes_hash: HexBytes = Web3.solidity_keccak(
        ["bytes"],
        [data],
    )

    return bytes_hash.hex()


def hash_assertion_with_indexes(
    leaves: list[str],
    hash_function: str | Callable[[str], HexStr] = solidity_keccak256,
    sort: bool = True,
) -> list[HexStr]:
    if sort:
        leaves.sort()

    return list(
        map(
            hash_function,
            [
                encode_packed(
                    ["bytes32", "uint256"],
                    [Web3.solidity_keccak(["string"], [leaf]), i],
                )
                for i, leaf in enumerate(leaves)
            ],
        )
    )


class MerkleTree:
    def __init__(
        self,
        leaves: list[str],
        hash_function: str | Callable[[str], HexStr] = solidity_keccak256,
        sort_leaves: bool = False,
        sort_pairs: bool = False,
    ):
        self.hash_function = self._set_hash_function(hash_function)
        self.sort_leaves = sort_leaves
        self.sort_pairs = sort_pairs
        self.leaves = self._process_leaves(leaves)
        self.tree = self.build_tree()

    @property
    def root(self) -> HexStr:
        return self.tree[0][0]

    def build_tree(self) -> list[list[HexStr]]:
        tree = [self.leaves]

        while len(level := tree[-1]) > 1:
            next_level = []
            for h1, h2 in zip(level[::2], level[1::2] + [None]):
                if h2:
                    next_level.append(
                        self.hash_function(
                            h1 + h2[2:]
                            if not self.sort_pairs
                            else "0x" + "".join(sorted([h1[2:], h2[2:]]))
                        )
                    )
                else:
                    next_level.append(h1)

            tree.append(next_level)

        tree.reverse()
        return tree

    def proof(self, leaf: HexStr, index: int | None = None) -> list[HexStr]:
        if index is None:
            for i, t_leaf in enumerate(self.leaves):
                if leaf == t_leaf:
                    index = i
                    break

        if index is None:
            raise LeafNotInTree(f"{leaf} is not a part of the Merkle Tree.")

        proof = []
        levels = copy.deepcopy(self.tree[:0:-1])
        for level in levels:
            if (len(level) % 2) == 1:
                level.append(level[-1])

            if (index % 2) == 1:
                proof.append(level[index - 1])
            else:
                proof.append(level[index + 1])

            index //= 2

        return proof

    def verify(self, proof: list[HexStr], leaf: HexStr) -> bool:
        if self.sort_pairs:
            hash = leaf
            for p in proof:
                if hash == p:
                    continue

                hash = self.hash_function("".join(sorted([hash, p])))

        else:
            for i, t_leaf in enumerate(self.leaves):
                if leaf == t_leaf:
                    index = i
                    break

            if index is None:
                raise LeafNotInTree(f"{leaf} is not a part of the Merkle Tree.")

            hash = leaf
            for p in proof:
                if hash == p:
                    continue

                is_left = (index % 2) == 0
                hash = self.hash_function("".join([hash, p] if is_left else [p, hash]))
                index //= 2

        return hash == self.root

    def _process_leaves(self, leaves: list[str | HexStr]) -> list[HexStr]:
        if self.sort_leaves:
            leaves.sort()

        return leaves

    def _set_hash_function(
        self, hash_function: str | Callable[[str], HexStr]
    ) -> Callable[[str], HexStr]:
        if (
            isinstance(hash_function, str)
            and hash_function in hashlib.algorithms_available
        ):
            return lambda data: getattr(hashlib, hash_function)(
                data.encode()
            ).hexdigest()
        elif isinstance(hash_function, Callable):
            return hash_function
        else:
            raise ValueError()
