"""PyCSL mock for Python's compression.zstd module — Low-level interface to compression and decompression routines in."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result == 0
def open(file: int, mode: int, level: int, options: int, __zstd_dict: int, encoding: int, errors: int) -> int:
    """Mock: Open a Zstandard-compressed file in binary or text mode, returning a :term:`file object`. The *file* argument can be eit..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def compress(data: int, level: int, options: int, zstd_dict: int) -> int:
    """Mock: Compress *data* (a :term:`bytes-like object`), returning the compressed data as a :class:`bytes` object. The *level* arg..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def decompress(data: int, zstd_dict: int, options: int) -> int:
    """Mock: Decompress *data* (a :term:`bytes-like object`), returning the uncompressed data as a :class:`bytes` object. The *option..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def train_dict(samples: int, dict_size: int) -> int:
    """Mock: Train a Zstandard dictionary, returning a :class:`ZstdDict` instance. Zstandard dictionaries enable more efficient compr..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def finalize_dict(zstd_dict: int, samples: int, dict_size: int, level: int) -> int:
    """Mock: An advanced function for converting a 'raw content' Zstandard dictionary into a regular Zstandard dictionary. 'Raw conte..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def get_frame_info(frame_buffer: int) -> int:
    """Mock: Retrieve a :class:`FrameInfo` object containing metadata about a Zstandard frame. Frames contain metadata related to the..."""
    return 0
