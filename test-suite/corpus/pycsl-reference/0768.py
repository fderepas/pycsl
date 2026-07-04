"""Test 0768 — NEGATIVE: a false string-content claim is REJECTED.

cleared-string.md §7 negative gate. `(a + b)[:len(a)]` provably equals `a`
(test 0765); the postcondition below FALSELY claims it equals `b`. The
content-faithful concat/slice model is honest — it must NOT prove this — so this
driver is expected to FAIL. It guards against the content laws collapsing into a
vacuous / over-strong axiom (which would let any string equal any other).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ ensures \result == b
#@ assigns \nothing
def wrong_prefix(a: str, b: str) -> str:
    return (a + b)[:len(a)]
