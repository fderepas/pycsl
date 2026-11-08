"""Test 0857 — WL-05c (T7) regression lock (NEGATIVE / SOUNDNESS TWIN): a caller-visible
`del d[k]` that CLAIMS the deleted key survives must FAIL. # pycsl-expected: FAIL

wrong-lowering-to-fix.md §WL-05c (soundness twin of 0855). The `writes {d}` frame is
genuinely CHECKED: a standalone param mutator that DELETES `d["a"]` but falsely asserts
`#@ ensures "a" in d` (the key still present after its own deletion) must NOT prove. If
this ever produced "Verification SUCCESS", the `del`→`map_update_none` model would be
UNSOUND (a false green for a caller-visible deletion). UNPROVABLE ⇒ XFAIL."""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Dict


#@ requires "a" in d
#@ ensures "a" in d
def del_dict_param_false(d: Dict[str, int]) -> None:
    del d["a"]
