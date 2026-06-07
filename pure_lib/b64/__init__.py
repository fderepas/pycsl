# pure_lib/b64 — pure-Python base64 module model
# Named 'b64' to avoid stdlib name clash.
#
# Contracts derived from library_reference/base64.rst.
# RST: "This module provides functions for encoding binary data to
#  printable ASCII characters and decoding such encodings back."
# RST: "b64encode(), b64decode(), b16encode(), b16decode()"
#
# Model: encoding/decoding as length transformations.
# Base64: 3 bytes → 4 chars, with padding. Decode is inverse.


#@ requires n >= 0
#@ ensures \result >= 0
#@ ensures n == 0 ==> \result == 0
#@ ensures n > 0 ==> \result >= 4
#@ assigns \nothing
def b64encode_len(n: int) -> int:
    """RST: 'Encode the bytes-like object s using Base64 and return
    the encoded bytes.' Output length = ceil(n/3) * 4."""
    if n == 0:
        return 0
    return ((n + 2) // 3) * 4


#@ requires n >= 0
#@ requires n % 4 == 0
#@ ensures \result >= 0
#@ ensures n == 0 ==> \result == 0
#@ ensures n > 0 ==> \result >= 1
#@ assigns \nothing
def b64decode_len(n: int) -> int:
    """RST: 'Decode the Base64 encoded bytes-like object.'
    Output length = n * 3 / 4 (without padding adjustment)."""
    if n == 0:
        return 0
    return (n // 4) * 3


#@ requires n >= 0
#@ ensures \result >= 0
#@ ensures \result == n * 2
#@ assigns \nothing
def b16encode_len(n: int) -> int:
    """RST: 'Encode the bytes-like object s using Base16.'
    Each byte → 2 hex chars."""
    return n * 2


#@ requires n >= 0
#@ requires n % 2 == 0
#@ ensures \result >= 0
#@ ensures \result == n // 2
#@ assigns \nothing
def b16decode_len(n: int) -> int:
    """RST: 'Decode the Base16 encoded bytes-like object.'
    Each 2 hex chars → 1 byte."""
    return n // 2


#@ requires n >= 0
#@ ensures \result >= 0
#@ ensures n == 0 ==> \result == 0
#@ assigns \nothing
def b32encode_len(n: int) -> int:
    """RST: 'Encode the bytes-like object s using Base32.'
    Output = ceil(n/5) * 8."""
    if n == 0:
        return 0
    return ((n + 4) // 5) * 8


#@ requires n >= 0
#@ requires n % 8 == 0
#@ ensures \result >= 0
#@ ensures n == 0 ==> \result == 0
#@ assigns \nothing
def b32decode_len(n: int) -> int:
    """RST: 'Decode the Base32 encoded bytes-like object.'
    Output = n * 5 / 8."""
    if n == 0:
        return 0
    return (n // 8) * 5


#@ requires n >= 0
#@ ensures \result >= 0
#@ ensures n == 0 ==> \result == 0
#@ ensures n > 0 ==> \result >= 4
#@ assigns \nothing
def urlsafe_b64encode_len(n: int) -> int:
    """RST: 'Encode bytes using URL-safe Base64 alphabet.'
    Same length as standard b64encode."""
    return b64encode_len(n)


#@ requires n >= 0
#@ requires n % 4 == 0
#@ ensures \result >= 0
#@ ensures n == 0 ==> \result == 0
#@ assigns \nothing
def urlsafe_b64decode_len(n: int) -> int:
    """RST: 'Decode bytes using URL-safe Base64 alphabet.'
    Same as standard b64decode."""
    return b64decode_len(n)
