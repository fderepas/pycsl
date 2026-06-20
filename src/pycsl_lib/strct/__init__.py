# pycsl_lib/strct — pure-Python struct module
# Named 'strct' to avoid stdlib name clash.
#
# Contracts derived from library_reference/struct.rst.
# RST: "Return the size of the struct corresponding to the format string."
# RST: "Return a bytes object containing the values packed according to format."
# RST: "Unpack from the buffer according to the format string.
#  The result is a tuple even if it contains exactly one item."
#
# Model: format string as int (its calcsize), buffer as list of int.


#@ requires fmt >= 0
#@ ensures \result >= 0
#@ ensures \result == fmt
def calcsize(fmt: int) -> int:
    """RST: 'Return the size of the struct corresponding to the format
    string format.' Size is non-negative."""
    return fmt


#@ requires fmt >= 0
#@ requires \length(buffer) >= fmt
#@ ensures \result >= 0
#@ ensures \result == fmt
#@ assigns \nothing
def pack(fmt: int, buffer: list, val: int) -> int:
    """RST: 'Return a bytes object containing the values packed according
    to the format string.' Result bytes length matches calcsize(fmt)."""
    return fmt


#@ requires fmt >= 0
#@ requires \length(buffer) >= fmt
#@ ensures \result >= 0
#@ ensures \result == fmt
#@ assigns \nothing
def unpack(fmt: int, buffer: list) -> int:
    """RST: 'Unpack from the buffer. The result is a tuple even if it
    contains exactly one item.' Returns number of values unpacked."""
    return fmt


#@ requires fmt >= 0
#@ requires offset >= 0
#@ requires \length(buffer) >= offset + fmt
#@ ensures \result >= 0
#@ ensures \result == fmt
#@ assigns \nothing
def unpack_from(fmt: int, buffer: list, offset: int) -> int:
    """RST: 'Unpack from buffer starting at position offset.'
    Returns number of values unpacked."""
    return fmt


#@ requires fmt >= 0
#@ requires offset >= 0
#@ requires \length(buffer) >= offset + fmt
#@ assigns buffer[offset .. offset + fmt]
#@ ensures \result == fmt
def pack_into(fmt: int, buffer: list, offset: int, val: int) -> int:
    """RST: 'Pack the values according to format and write the packed
    bytes into the writable buffer starting at position offset.'
    Returns bytes written."""
    return fmt


#@ requires fmt >= 0
#@ requires \length(buffer) >= fmt
#@ ensures \result >= 0
def iter_unpack(fmt: int, buffer: list) -> int:
    """RST: 'Iteratively unpack from the buffer according to the format string.'
    Returns number of iterations = len(buffer) // calcsize(fmt).
    Requires buffer length to be a multiple of fmt (precondition)."""
    if fmt == 0:
        return 0
    #@ assert fmt > 0
    return len(buffer) // fmt


# --- Struct class ---

""  # pycsl
#@ class invariant self._fmt >= 0
class Struct:
    """RST: 'Compiled representation of a format string.'"""

    def __init__(self):
        self._fmt = 0

    #@ requires fmt >= 0
    #@ ensures self._fmt == fmt
    #@ assigns self._fmt
    def set_format(self, fmt: int) -> None:
        """Set the struct format (calcsize value)."""
        self._fmt = fmt

    #@ ensures \result >= 0
    #@ ensures \result == self._fmt
    #@ assigns \nothing
    def size(self) -> int:
        """RST: 'The calculated size of the struct, corresponding to format.'"""
        return self._fmt

    #@ requires \length(buffer) >= self._fmt
    #@ ensures \result == self._fmt
    #@ assigns \nothing
    def pack(self, buffer: list, val: int) -> int:
        """RST: 'Works like pack(), using the compiled format.'"""
        return self._fmt

    #@ requires \length(buffer) >= self._fmt
    #@ ensures \result == self._fmt
    #@ assigns \nothing
    def unpack(self, buffer: list) -> int:
        """RST: 'Works like unpack(), using the compiled format.'"""
        return self._fmt

    #@ requires offset >= 0
    #@ requires \length(buffer) >= offset + self._fmt
    #@ ensures \result == self._fmt
    #@ assigns \nothing
    def unpack_from(self, buffer: list, offset: int) -> int:
        """RST: 'Works like unpack_from(), using the compiled format.'"""
        return self._fmt

    #@ requires offset >= 0
    #@ requires \length(buffer) >= offset + self._fmt
    #@ ensures \result == self._fmt
    #@ assigns buffer[offset .. offset + self._fmt]
    def pack_into(self, buffer: list, offset: int, val: int) -> int:
        """RST: 'Works like pack_into(), using the compiled format.'"""
        return self._fmt
