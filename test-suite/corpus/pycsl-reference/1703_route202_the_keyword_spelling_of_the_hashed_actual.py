r"""Test 1703 - ROUTE #200/#202 carrier, the KEYWORD spelling (gen #30): route #200's first repair walked the IR's `args` list only. Keyword actuals live in a SEPARATE slot - `{"type": "Call", "func": "callee", "args": [], "keywords": [{"arg": "p", "value": {"type": "String", ...}}]}` - so a check that reads `args` sees an EMPTY argument list and waves the call through. `callee(p="a")` against a DECLARED `p: int` therefore still emitted `(callee 747471683)` and PROVED `\result == 1` while CPython answers 2. This is gen #30's own lesson (i) - "name WHICH SPELLINGS were run" - missed on the repair that banked it, one hour later. The refusal now binds keyword actuals BY NAME, which needs no positional offset and no vararg adjustment. This file must FAIL.
"""
# pycsl-expected: FAIL

_ = 0  # anchor


#@ requires True
#@ ensures p == 747471683 ==> \result == 1
#@ ensures p != 747471683 ==> \result == 2
def callee(p: int) -> int:
    if p == 747471683:
        return 1
    return 2


#@ ensures \result == 1
def probe() -> int:
    return callee(p="a")
