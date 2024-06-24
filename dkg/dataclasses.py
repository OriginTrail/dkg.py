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

from dataclasses import dataclass
from enum import auto, Enum

import pandas as pd

from dkg.types import AutoStrEnum, AutoStrEnumCapitalize, AutoStrEnumUpperCase


class BlockchainResponseDict(dict):
    pass


class HTTPRequestMethod(Enum):
    GET = 1
    POST = 2


class NodeResponseDict(dict):
    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(self)


class BidSuggestionRange(AutoStrEnum):
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()
    ALL = auto()


class KnowledgeAssetEnumStates(AutoStrEnumUpperCase):
    LATEST = auto()
    LATEST_FINALIZED = auto()


class KnowledgeAssetContentVisibility(AutoStrEnumUpperCase):
    ALL = auto()
    PUBLIC = auto()
    PRIVATE = auto()


class ParanetIncentivizationType(AutoStrEnumCapitalize):
    NEUROWEB = auto()


@dataclass
class BaseIncentivesPoolParams:
    def to_contract_args(self) -> dict:
        raise NotImplementedError("This method should be overridden in subclasses")
