import copy
import hashlib
from typing import Callable

from dkg.exceptions import LeafNotInTree
from dkg.types import HexStr
from eth_abi.packed import encode_packed
from web3 import Web3


def solidity_keccak256(hash: HexStr) -> HexStr:
    """
    Computes the Keccak-256 hash of the given hex string, as used in Solidity.

    Args:
        hash (HexStr): The hex string to be hashed.

    Returns:
        HexStr: The Keccak-256 hash of the input hex string.
    """
    return bytes(
        Web3.solidity_keccak(
            ["bytes"],
            ["0x" + hash],
        )
    ).hex()


def hash_assertion_with_indexes(
    leaves: list[str],
    hash_function: str | Callable[[str], HexStr] = solidity_keccak256,
    sort: bool = True,
) -> list[HexStr]:
    """
    Hashes the given assertions with their respective indexes.

    Args:
        leaves (list[str]): The list of assertions to be hashed.
        hash_function (str | Callable[[str], HexStr], optional): The hash function to use.
        Defaults to solidity_keccak256.
        sort (bool, optional): Whether to sort the leaves before hashing. Defaults to True.

    Returns:
        list[HexStr]: The list of hashed assertions with their indexes.
    """
    if sort:
        leaves.sort()

    return list(
        map(
            hash_function,
            [
                encode_packed(
                    ["bytes32", "uint256"],
                    [Web3.solidity_keccak(["string"], [leaf]), i],
                ).hex()
                for i, leaf in enumerate(leaves)
            ],
        )
    )


class MerkleTree:
    """
    Represents a Merkle Tree data structure.

    Attributes:
        leaves (list[str]): The leaf nodes of the tree.
        tree (list[list[HexStr]]): The Merkle Tree structure.
        root (HexStr): The root hash of the Merkle Tree.
    """

    def __init__(
        self,
        leaves: list[str],
        hash_function: str | Callable[[str], HexStr] = solidity_keccak256,
        sort_leaves: bool = False,
        sort_pairs: bool = False,
    ):
        """
        Initializes a MerkleTree instance with the given leaves and hash function.

        Args:
            leaves (list[str]): The leaf nodes of the tree.
            hash_function (str | Callable[[str], HexStr], optional): The hash function to use.
            Defaults to solidity_keccak256.
            sort_leaves (bool, optional): Whether to sort the leaves before building the tree.
            Defaults to False.
            sort_pairs (bool, optional): Whether to sort the pairs when building the tree.
            Defaults to False.
        """
        self.hash_function = self._set_hash_function(hash_function)
        self.sort_leaves = sort_leaves
        self.sort_pairs = sort_pairs
        self.leaves = self._process_leaves(leaves)
        self.tree = self.build_tree()

    @property
    def root(self) -> HexStr:
        """
        Returns the root hash of the Merkle Tree.

        Returns:
            HexStr: The root hash of the Merkle Tree.
        """
        return self.tree[0][0]

    def build_tree(self) -> list[list[HexStr]]:
        """
        Builds the Merkle Tree structure from the leaf nodes.

        Returns:
            list[list[HexStr]]: The Merkle Tree structure.
        """
        tree = [self.leaves]

        while len(level := tree[-1]) > 1:
            next_level = []
            for h1, h2 in zip(level[::2], level[1::2] + [None]):
                if h2:
                    next_level.append(
                        self.hash_function(
                            "".join(
                                [h1, h2] if not self.sort_pairs else sorted([h1, h2])
                            )
                        )
                    )
                else:
                    next_level.append(h1)

            tree.append(next_level)

        tree.reverse()
        return tree

    def proof(self, leaf: HexStr, index: int | None = None) -> list[HexStr]:
        """
        Generates a Merkle proof for the given leaf.

        Args:
            leaf (HexStr): The leaf for which to generate the proof.
            index (int | None, optional): The index of the leaf in the tree. If not provided,
            it will be determined automatically. Defaults to None.

        Returns:
            list[HexStr]: The Merkle proof for the given leaf.

        Raises:
            LeafNotInTree: If the given leaf is not found in the tree.
        """
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
        """
        Verifies a Merkle proof for the given leaf.

        Args:
            proof (list[HexStr]): The Merkle proof to verify.
            leaf (HexStr): The leaf for which to verify the proof.

        Returns:
            bool: True if the proof is valid, False otherwise.

        Raises:
            LeafNotInTree: If the given leaf is not found in the tree.
        """
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
        """
        Processes the leaves before building the Merkle Tree.

        Args:
            leaves (list[str | HexStr]): The list of leaves to be processed.

        Returns:
            list[HexStr]: The processed list of leaves.
        """
        if self.sort_leaves:
            leaves.sort()

        return leaves

    def _set_hash_function(
        self, hash_function: str | Callable[[str], HexStr]
    ) -> Callable[[str], HexStr]:
        """
        Sets the hash function to be used in the Merkle Tree.

        Args:
            hash_function (str | Callable[[str], HexStr]): The hash function to use.

        Returns:
            Callable[[str], HexStr]: The hash function.

        Raises:
            ValueError: If the provided hash_function is neither a string nor a callable.
        """
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
