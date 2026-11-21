r"""Test 1868 — gen #31: `#@ reveal` carries the DEFINITION-fact across the import.

Byte-identical to 1867 except for the line `#@ reveal pack16`. annotations.md §2.10 row 2:
"Within the owning unit it is a no-op (the definition is the visible `let`); ACROSS MODULES
IT CITES THE EXPORTED DEFINITION-FACT." The first clause was true by construction; the
second had no implementation, so both halves of this pair used to fail and their emitted
`.mlw` files were byte-identical.

THE SCOPE IS THE MODULE, and that is wider than the sentence says: the `val` stub for an
imported function is emitted ONCE per importing module, so "this caller opts in AT THIS
SITE" cannot be expressed by a single stub. If ANY function in the importing module
reveals `<fn>`, the stub shows the DEFINITION. That is strictly MORE information than the
interface and sound for the same reason the narrowing VC is — the definition is a fact the
owning unit PROVED about the same `let`. The per-site form needs a second `val` plus
call-site rewriting and is recorded as the refinement rather than built.
"""
# pycsl-expected: PASS
from multi_file_lib.opaque_pack import pack16

_ = 0  # anchor


#@ reveal pack16
#@ requires 0 <= x and x <= 65535
#@ assigns \nothing
#@ ensures \result == x
def caller(x: int) -> int:
    d = pack16(x)
    return d[0] * 256 + d[1]
