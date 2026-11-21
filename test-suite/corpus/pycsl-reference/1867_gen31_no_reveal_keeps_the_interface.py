r"""Test 1867 — gen #31: WITHOUT `#@ reveal`, the importer sees only the INTERFACE.

The control half of the `#@ reveal` pair, and the half that must keep failing. `pack16` in
`multi_file_lib.opaque_pack` has a rich DEFINITION (`\result[0]*256 + \result[1] == a`) and
a narrow `#@ interface ensures \length(\result) == 2`. This caller needs the definition's
fact and does not ask for it, so the import stub carries only

    val pack16 (a: int) : array int
      requires { ((0 <= a) && (a <= 65535)) }
      ensures  { ((Array.length result) = 2) }

and `\result == x` is correctly unprovable. That is opacity working as designed.

Its twin `1868` adds `#@ reveal pack16` and verifies. Before gen #31 BOTH halves failed and
the two emitted `.mlw` files were BYTE-IDENTICAL, because `#@ reveal` was parsed, woven onto
`node.csl_reveal`, written into the IR as `func_ir["reveal"]` and read by no Module-6
consumer — so `#@ interface` was a trapdoor with no way back out.
"""
# pycsl-expected: FAIL
from multi_file_lib.opaque_pack import pack16

_ = 0  # anchor


#@ requires 0 <= x and x <= 65535
#@ assigns \nothing
#@ ensures \result == x
def caller(x: int) -> int:
    d = pack16(x)
    return d[0] * 256 + d[1]
