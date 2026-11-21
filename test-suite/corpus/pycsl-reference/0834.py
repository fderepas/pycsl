"""Test 0834 — WL-05b regression lock (NEGATIVE): a FALSE post-mutation claim must FAIL. # pycsl-expected: FAIL

wrong-lowering-to-fix.md §WL-05b (soundness twin of 0820/0832). The caller-visible
`writes {d}` frame is genuinely CHECKED: a dict param mutator that writes one value but
CLAIMS a different post-state must NOT prove. Here the body writes `d["a"] = 5` but the
contract falsely asserts `#@ ensures d["a"] == 6`. If this ever produced a
"Verification SUCCESS" the ref/writes model would be UNSOUND (a false green for a
mutation that computes a different value). The proof is UNPROVABLE ⇒ XFAIL — proving
the model is not vacuous and the frame constrains the post-state faithfully.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import Dict


#@ ensures d["a"] == 6
def mutate_dict_param_false(d: Dict[str, int]) -> int:
    d["a"] = 5
    return d["a"]
