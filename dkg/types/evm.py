from typing import NewType

from .encoding import DataHexStr

Address = NewType("Address", DataHexStr)
ChecksumAddress = NewType("ChecksumAddress", DataHexStr)

Wei = NewType("Wei", int)
