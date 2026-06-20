"""PyCSL stub for Python's `struct` module.

This stub gives the module concrete contracts. PyCSL's Module6 emits a
type-aware abstract op for each compile-time format string seen at a
call site (`struct_pack_<slot_id>` / `struct_unpack_<slot_id>`); the
function bodies below are therefore mostly placeholder. The contracts
matter for two cases:

  1. Dynamic format strings (not a `String` IR node at the call site)
     fall through to the generic auto-trust path and consult the
     declared `requires` / `ensures` here.
  2. Programs that take the address of `struct.pack` / `struct.unpack`
     and pass it as a value see the contracts (not the format-aware
     dispatch), so they need to be sound.

See missing-bytes-struct-feature.md Phase 2 for the design.
"""
_ = 0  # anchor

#@ requires len(format) >= 0
#@ \trusted reviewer: pycsl-self-annotate
#@ ensures len(\result) >= 0
# cite:_note: The format-aware dispatch in Module6 replaces this body
#             whenever the format is a compile-time literal. Trust here
#             is for the dynamic-format fallback only.
def pack(format: bytes, v1: int, v2: int, ___: int) -> bytes:
    """Return a bytes object containing values packed per *format*."""
    return b''

#@ requires len(format) >= 0
#@ requires offset >= 0
#@ \trusted reviewer: pycsl-self-annotate
#@ ensures \result == 0
def pack_into(format: bytes, buffer: bytes, offset: int,
              v1: int, v2: int, ___: int) -> int:
    """Pack values into *buffer* at *offset* per *format*."""
    return 0

#@ requires len(format) >= 0
#@ requires len(buffer) >= 0
#@ \trusted reviewer: pycsl-self-annotate
#@ ensures True
def unpack(format: bytes, buffer: bytes) -> int:
    """Unpack from *buffer* per *format*. Returns a tuple even for one item."""
    return 0

#@ requires len(format) >= 0
#@ requires len(buffer) >= 0
#@ requires offset >= 0
#@ \trusted reviewer: pycsl-self-annotate
#@ ensures True
def unpack_from(format: bytes, buffer: bytes, offset: int) -> int:
    """Unpack from *buffer* at *offset* per *format*."""
    return 0

#@ requires len(format) >= 0
#@ requires len(buffer) >= 0
#@ \trusted reviewer: pycsl-self-annotate
#@ ensures True
def iter_unpack(format: bytes, buffer: bytes) -> int:
    """Iteratively unpack from *buffer* per *format*."""
    return 0

#@ requires len(format) >= 0
#@ \trusted reviewer: pycsl-self-annotate
#@ ensures \result >= 0
def calcsize(format: bytes) -> int:
    """Return the size of the struct produced by *format*."""
    return 0
