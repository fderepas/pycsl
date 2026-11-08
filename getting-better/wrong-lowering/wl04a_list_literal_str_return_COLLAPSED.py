"""WL-04a — `-> List[str]` RETURN built by a LIST LITERAL — **FIXED**.

Before: `return ["a", "b"]` built `Array.make 2 (747471683)` (hashed `array int`)
while the `-> List[str]` annotation typed the return `array string` — a mismatch
(Detector D2: TYPEERR); the contract `\result[0]` used the opaque `subscript_get`.

After (wrong-lowering-to-fix.md §WL-04a): the literal is built as `array string`
and `\result[i]` on the array return lowers to a native `Array.get`. Verdict: PROVEN."""
_ = 0
from typing import List


#@ ensures \result[0] == "a"
#@ ensures \result[1] == "b"
def f() -> List[str]:
    return ["a", "b"]
