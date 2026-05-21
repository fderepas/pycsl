"""PyCSL mock for Python's binascii module — Tools for converting between binary and various ASCII-encoded binary."""
_ = 0  # anchor

#@ \trusted
#@ ensures \result >= 0
def a2b_uu(string: int) -> int:
    """Mock: Convert a single line of uuencoded data back to binary and return the binary data. Lines normally contain 45 (binary) by..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def b2a_uu(data: int, backtick: int) -> int:
    """Mock: Convert binary data to a line of ASCII characters, the return value is the converted line, including a newline char. The..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def a2b_base64(string: int, padded: int, alphabet: int, strict_mode: int, canonical: int) -> int:
    """Mock: Convert a block of base64 data back to binary and return the binary data. More than one line may be passed at a time. Op..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def b2a_base64(data: int, padded: int, alphabet: int, wrapcol: int, newline: int) -> int:
    """Mock: Convert binary data to a line(s) of ASCII characters in base64 coding, as specified in :rfc:`4648`. If *padded* is true ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def a2b_ascii85(string: int, foldspaces: int, adobe: int, ignorechars: int, canonical: int) -> int:
    """Mock: Convert Ascii85 data back to binary and return the binary data. Valid Ascii85 data contains characters from the Ascii85 ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def b2a_ascii85(data: int, foldspaces: int, wrapcol: int, pad: int, adobe: int) -> int:
    """Mock: Convert binary data to a formatted sequence of ASCII characters in Ascii85 coding. The return value is the converted dat..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def a2b_base85(string: int, alphabet: int, ignorechars: int, canonical: int) -> int:
    """Mock: Convert Base85 data back to binary and return the binary data. More than one line may be passed at a time. Valid Base85 ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def b2a_base85(data: int, alphabet: int, wrapcol: int, pad: int) -> int:
    """Mock: Convert binary data to a line of ASCII characters in Base85 coding. The return value is the converted line. Optional *al..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def a2b_base32(string: int, padded: int, alphabet: int, ignorechars: int, canonical: int) -> int:
    """Mock: Convert base32 data back to binary and return the binary data. Valid base32 data contains characters from the base32 alp..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def b2a_base32(data: int, padded: int, alphabet: int, wrapcol: int) -> int:
    """Mock: Convert binary data to a line of ASCII characters in base32 coding, as specified in :rfc:`4648`. The return value is the..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def a2b_qp(data: int, header: int) -> int:
    """Mock: Convert a block of quoted-printable data back to binary and return the binary data. More than one line may be passed at ..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def b2a_qp(data: int, quotetabs: int, istext: int, header: int) -> int:
    """Mock: Convert binary data to a line(s) of ASCII characters in quoted-printable encoding.  The return value is the converted li..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def crc_hqx(data: int, value: int) -> int:
    """Mock: Compute a 16-bit CRC value of *data*, starting with *value* as the initial CRC, and return the result.  This uses the CR..."""
    return 0

#@ \trusted
#@ ensures \result == 0
def crc32(data: int, value: int) -> int:
    """Mock: Compute CRC-32, the unsigned 32-bit checksum of *data*, starting with an initial CRC of *value*.  The default initial CR..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def b2a_hex(data: int, sep: int, bytes_per_sep: int) -> int:
    """Mock: Return the hexadecimal representation of the binary *data*.  Every byte of *data* is converted into the corresponding 2-..."""
    return 0

#@ \trusted
#@ ensures \result >= 0
def a2b_hex(hexstr: int, ignorechars: int) -> int:
    """Mock: Return the binary data represented by the hexadecimal string *hexstr*.  This function is the inverse of :func:`b2a_hex`...."""
    return 0
