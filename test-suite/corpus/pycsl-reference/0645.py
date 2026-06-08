"""Test 0645 — str local variable binding (07-2333-rev2 TP-1 / Gap 1).

A `str`-annotated local must lower to a string ref (`let r = ref "ab" in`), not the integer default
`ref 0` — the local counterpart of the str-param lowering. The unified type environment (Γ_w) carries
the string class for locals, so `r: str = "ab"; return r` binds and proves. (Closes the 08-0350 astmod
Phase 1 blocker: `r: str = dump(...)` can now bind a str local.)
"""
# pycsl-flags: --memory-model hoare


#@ ensures \result == "ab"
#@ assigns \nothing
def test() -> str:
    r: str = "ab"
    return r
