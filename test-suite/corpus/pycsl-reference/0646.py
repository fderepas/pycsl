"""Test 0646 — str local bound from a str parameter (07-2333-rev2 TP-1)."""
# pycsl-flags: --memory-model hoare


#@ ensures \result == s
#@ assigns \nothing
def via(s: str) -> str:
    r: str = s
    return r
