# Formal tests for pure_lib/zl — zlib module
from pure_lib.zl import compress, decompress, crc32, adler32


#@ requires data >= 0
#@ ensures \result >= 0
def test_compress_nonneg(data: int) -> int:
    """compress returns non-negative."""
    return compress(data)


#@ requires data >= 0
#@ ensures \result >= 0
def test_decompress_nonneg(data: int) -> int:
    """decompress returns non-negative."""
    return decompress(data)


#@ requires data >= 0
#@ ensures \result >= 0
def test_crc32_nonneg(data: int) -> int:
    """crc32 returns non-negative."""
    return crc32(data)
