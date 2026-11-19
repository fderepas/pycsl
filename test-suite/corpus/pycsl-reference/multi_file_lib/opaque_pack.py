"""multi_file_lib.opaque_pack — Track B opacity fixture (cross-module `#@ interface`).

`pack16` carries TWO contracts: the rich DEFINITION (`\result[0]*256 + \result[1] == a`,
verified against the body) and a narrow `#@ interface ensures \length(\result) == 2`, which
is all an importer sees by default. The narrowing VC `pack16__narrows_ens_0` proves in the
owning unit — the interface is a sound WEAKENING of the definition.

Used by `1867` (importer WITHOUT `#@ reveal`, expected FAIL) and `1868` (importer WITH it,
expected PASS): the pair is what shows `#@ reveal` carries the definition-fact across the
module boundary, which §2.10 promised and nothing implemented until gen #31.
"""
_ = 0  # anchor


#@ requires 0 <= a and a <= 65535
#@ assigns \nothing
#@ ensures \length(\result) == 2
#@ ensures \result[0] * 256 + \result[1] == a
#@ interface ensures \length(\result) == 2
def pack16(a: int) -> list:
    return bytes([a // 256, a % 256])
