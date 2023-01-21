from typing import NewType

HexStr = NewType("HexStr", str)
DataHexStr = NewType("DataHexStr", str)
BytesLike = bytes | DataHexStr
