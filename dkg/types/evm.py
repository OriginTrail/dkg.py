from .encoding import DataHexStr
from typing import NewType

Address = NewType('Address', DataHexStr)
ChecksumAddress = NewType('ChecksumAddress', DataHexStr)

Wei = NewType('Wei', int)
