r"""Test 10280 -- lvZ2 restricted Path type separation (expected FAIL): a modelled `Path(<str>)`
passed through the IMPORTED `ident(p: Path) -> Fp` (`Fp = TypeAliasType("Fp", Path)`, red team
rt70 m24, INTRODUCED by batch C: the string lowering decided `q == str(q)`); CPython: False. The
modelled value is now the abstract `py_path`, the imported parameter a `string`: a Why3 TYPE
ERROR (fail-closed).
"""
# pycsl-expected: FAIL
from __future__ import annotations
from pathlib import Path
from multi_file_lib.lvz2_pathlib import ident


#@ ensures \result == True
#@ assigns \nothing
def f(s: str) -> bool:
    q = ident(Path(s))
    return q == str(q)


if __name__ == "__main__":
    r = f("a")
    print("VIOLATION contract" if r is not True else "result", r)
