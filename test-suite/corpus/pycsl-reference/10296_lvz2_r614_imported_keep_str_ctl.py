r"""Test 10296 -- R614 unresolved aliases / unknown callees (lvZ2, run #8; expected PASS): a `str`
passed to the imported `keep(x: str) -> str` of the same helper is admitted, its result compared as a
string (CPython: True). The helper's `TypeAliasType` alias does not taint a str flow. (No `assigns` claim: the
injected stub `keep` declares no frame, so the typed / store models let it write the heap.)
"""
# pycsl-expected: PASS
from __future__ import annotations
from multi_file_lib.lvz2r_tat import keep


#@ ensures \result == True
def f(s: str) -> bool:
    q = keep(s)
    return q == q


if __name__ == "__main__":
    r = f("a")
    print("VIOLATION contract" if r is not True else "result", r)
