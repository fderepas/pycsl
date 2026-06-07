# Pure model for zlib — compression
# Models compression as size transformation.


#@ requires data_len >= 0
#@ ensures \result >= 0
def compress(data_len: int) -> int:
    """Compress data. Output may be smaller or larger."""
    return data_len


#@ requires data_len >= 0
#@ ensures \result >= data_len
def decompress(data_len: int) -> int:
    """Decompress data. Output >= input (decompressed is larger)."""
    return data_len


#@ requires data_len >= 0
#@ ensures \result >= 0
def crc32(data_len: int) -> int:
    """Compute CRC-32 checksum. Returns non-negative int."""
    return 0


#@ requires data_len >= 0
#@ ensures \result >= 0
def adler32(data_len: int) -> int:
    """Compute Adler-32 checksum. Returns non-negative int."""
    return 0


# Compression levels
Z_NO_COMPRESSION: int = 0
Z_BEST_SPEED: int = 1
Z_BEST_COMPRESSION: int = 9
Z_DEFAULT_COMPRESSION: int = -1
