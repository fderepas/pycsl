"""PyCSL mock for Python's zlib module — Low-level interface to compression and decompression routines."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def adler32(data: int, value: int) -> int:
    """Mock: Computes an Adler-32 checksum of *data*.  (An Adler-32 checksum is almost as reliable as a CRC32 but can be computed muc..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def adler32_combine(adler1: int, adler2: int, len2: int) -> int:
    """Mock: Combine two Adler-32 checksums into one. Given the Adler-32 checksum *adler1* of a sequence ``A`` and the Adler-32 check..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def compress(data: int, level: int, wbits: int) -> int:
    """Mock: Compresses the bytes in *data*, returning a bytes object containing compressed data. *level* is an integer from ``0`` to..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def compressobj(level: int, method: int, wbits: int, memLevel: int, strategy: int, zdict: int) -> int:
    """Mock: Returns a compression object, to be used for compressing data streams that won't fit into memory at once. *level* is the..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def crc32(data: int, value: int) -> int:
    """Mock: .. index:: single: Cyclic Redundancy Check single: checksum; Cyclic Redundancy Check Computes a CRC (Cyclic Redundancy C..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def crc32_combine(crc1: int, crc2: int, len2: int) -> int:
    """Mock: Combine two CRC-32 checksums into one. Given the CRC-32 checksum *crc1* of a sequence ``A`` and the CRC-32 checksum *crc..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def decompress(data: int, wbits: int, bufsize: int) -> int:
    """Mock: Decompresses the bytes in *data*, returning a bytes object containing the uncompressed data.  The *wbits* parameter depe..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def decompressobj(wbits: int, zdict: int) -> int:
    """Mock: Returns a decompression object, to be used for decompressing data streams that won't fit into memory at once. The *wbits..."""
    return 0
