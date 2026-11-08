def g(x: int) -> int:
    import struct
    return len(struct.pack('B', 300 * x))
