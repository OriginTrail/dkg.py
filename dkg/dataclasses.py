from enum import Enum

import pandas as pd


class BlockchainResponseDict(dict):
    pass


class HTTPRequestMethod(Enum):
    GET = 1
    POST = 2


class NodeResponseDict(dict):
    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self)


class KnowledgeAssetEnumStates(Enum):
    LATEST = "LATEST"
    LATEST_FINALIZED = "LATEST_FINALIZED"


class KnowledgeAssetContentVisibility(Enum):
    ALL = "ALL"
    PUBLIC = "PUBLIC"
    PRIVATE = "PRIVATE"
