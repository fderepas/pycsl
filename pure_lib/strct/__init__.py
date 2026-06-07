# pure_lib/strct — pure-Python struct module model
# Named 'strct' to avoid stdlib name clash.
#
# Models struct.calcsize, pack, unpack as length contracts.
# Contract-only: the real implementation is C (_struct).


#@ requires fmt >= 0
#@ ensures \result >= 0
def calcsize(fmt: int) -> int:
    """Return the size of the struct described by format string.
    Model: format code count → byte size (non-negative)."""
    return fmt


#@ requires fmt >= 0
#@ ensures \result >= 0
def pack(fmt: int, val: int) -> int:
    """Pack values into bytes according to format.
    Model: result length = calcsize(fmt)."""
    return fmt


#@ requires fmt >= 0
#@ requires data >= 0
#@ ensures \result >= 0
def unpack(fmt: int, data: int) -> int:
    """Unpack bytes according to format. Returns tuple length.
    Model: result count = number of format codes."""
    return fmt


#@ requires fmt >= 0
#@ requires buffer >= 0
#@ requires offset >= 0
#@ ensures \result >= 0
def unpack_from(fmt: int, buffer: int, offset: int) -> int:
    """Unpack from buffer at offset. Returns tuple length."""
    return fmt


#@ requires fmt >= 0
#@ ensures \result >= 0
def pack_into(fmt: int, buffer: int, offset: int, val: int) -> int:
    """Pack into buffer at offset. Returns bytes written."""
    return fmt
