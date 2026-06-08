"""Test 0640 — `literal_eval` of a constant literal is faithful (07-1839 P5c).

`ast.literal_eval("-5")` on a compile-time-constant argument is evaluated at verification time with
host `ast.literal_eval` (the source of truth) and emitted as the actual value `-5` with its true
type — so `\result == -5` proves. Supersedes the opaque/unsound `>= 0` handle for the constant case.
"""
# pycsl-flags: --memory-model hoare


#@ ensures \result == -5
#@ assigns \nothing
def f() -> int:
    return ast.literal_eval("-5")
