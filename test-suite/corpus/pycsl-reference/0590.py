"""Test 0590 — cross-module call fidelity: real types, constant value, default fill (1111-spec R5+R6+R7).

`run` calls the imported `clamp_seek("f", SEEK_SET)`. Three no-more-int fixes combine:
  - R5: the string literal `"f"` flows into `clamp_seek`'s `name: str` parameter as a Why3
    `string`, NOT an int hash (the prior behaviour `(clamp_seek 302… …)` was a type error
    against `(name: string)`).
  - R6: the imported constant `SEEK_SET` folds to its literal `0`, so the callee precondition
    `how >= 0 and how <= 2` discharges (a value-less `val constant` left `how` unknown).
  - R7: the omitted trailing `mode` (default `7`) is filled at the call site, so the
    application is total (was a partial-application type error).
RED on the prior commit (the string type error fires first).
"""
# pycsl-flags: --memory-model hoare
from multi_file_lib.r1111_stub import clamp_seek, SEEK_SET


#@ ensures \result == 0
#@ assigns \nothing
def run() -> int:
    return clamp_seek("f", SEEK_SET)
