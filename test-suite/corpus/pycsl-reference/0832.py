"""Test 0832 — WL-05b regression lock (POSITIVE): dict-PARAM mutation ESCAPES to the caller.

wrong-lowering-to-fix.md §WL-05b (caller-visibility). The whole point of the faithful
model: a dict passed to a mutator is mutated BY REFERENCE, so the write is visible to
the caller. `put` takes `d: Dict[str,int]`, item-mutates it (`d["a"] = 5`) and states
the post-state in its contract (`#@ ensures d["a"] == 5`, which reads `Map.get !d "a"`
after the `writes {d}` frame). `caller` allocates a LOCAL dict `d` (a `ref`), calls
`put(d)` — the call site passes the BARE ref `d`, not the dereferenced value `!d`, so
the mutation escapes — and then reads `d["a"]`, which the callee's `ensures` proves is
`5`. If the call site passed `!d` (by value) this would TYPEERR or the mutation would
be lost; PROVEN here confirms the escape is both well-typed and sound.
"""
_ = 0  # anchor
from typing import Dict


#@ ensures d["a"] == 5
def put(d: Dict[str, int]) -> None:
    d["a"] = 5


#@ ensures \result == 5
def caller() -> int:
    d: Dict[str, int] = {}
    put(d)
    return d["a"]
