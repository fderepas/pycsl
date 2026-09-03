"""Test 0975 — a `#@` directive on an anchor that does not consume it is REFUSED.

Every attachment site in `Module3_Weaver` is an `if/elif` chain with NO `else`, so a
directive that reached an anchor whose site did not name its class was DROPPED — silently,
while the run still printed *All contracts formally proven*. Measured, before the refusal:

    #@ assert 1 == 2                       <-- FALSE, AND NEVER CHECKED
    #@ ensures \result == 0
    def f() -> int:
        return 0
    [+] Verification SUCCESS! All contracts formally proven.

The same held for `#@ assert 1 == 2` above a `class` and for `#@ ensures 1 == 2` on a
`while`. `Module3_Weaver._reject_misplaced_directives` now refuses them, from the
`\trusted` `process` choke point that both Module 3 entry paths go through.

LIVE VICTIMS FOUND BY THE CENSUS THAT MOTIVATED IT, all repaired in place:
`pycsl_lib/re/_engine.py` had TWO `#@ class invariant` below `__slots__`, landing on
`__init__`, so `ReMatch` carried NO invariant at all; and
`pycsl_lib/os/UnixInodeFileSystem._pad_name` had an `#@ assigns` and THREE `#@ ensures`
after its docstring, with a source comment claiming they were "surfaced as top-level
ensures" — they were surfaced nowhere.

This file is `pycsl-expected: FAIL`: the refusal IS the expected verdict.
"""
# pycsl-expected: FAIL


#@ assert 1 == 2
#@ requires True
#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    return 0
