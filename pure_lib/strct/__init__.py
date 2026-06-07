# pure_lib/strct — pure-Python struct module model
# Named 'strct' to avoid stdlib name clash.
#
# Contracts derived from library_reference/struct.rst.
# RST: "Return the size of the struct corresponding to the format string."
# RST: "Return a bytes object containing the values packed according to format."
# RST: "Unpack from the buffer according to the format string.
#  The result is a tuple even if it contains exactly one item."


#@ requires fmt >= 0
#@ ensures \result >= 0
def calcsize(fmt: int) -> int:
    """RST: 'Return the size of the struct corresponding to the format
    string format.' Size is non-negative."""
    return fmt


#@ requires fmt >= 0
#@ ensures \result >= 0
def pack(fmt: int, val: int) -> int:
    """RST: 'Return a bytes object containing the values packed according
    to the format string.' Result bytes length matches calcsize(fmt)."""
    return fmt


#@ requires fmt >= 0
#@ requires data >= 0
#@ ensures \result >= 0
def unpack(fmt: int, data: int) -> int:
    """RST: 'Unpack from the buffer. The result is a tuple even if it
    contains exactly one item.' Returns tuple length (number of format codes)."""
    return fmt


#@ requires fmt >= 0
#@ requires buffer >= 0
#@ requires offset >= 0
#@ ensures \result >= 0
def unpack_from(fmt: int, buffer: int, offset: int) -> int:
    """RST: 'Unpack from buffer starting at position offset.'
    Returns tuple length."""
    return fmt


#@ requires fmt >= 0
#@ ensures \result >= 0
def pack_into(fmt: int, buffer: int, offset: int, val: int) -> int:
    """RST: 'Pack the values according to format and write the packed
    bytes into the writable buffer starting at position offset.'
    Returns bytes written."""
    return fmt
