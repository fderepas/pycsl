"""WL-05 baseline (NOT a finding) — a LOCAL dict write-read-back proves faithfully."""
_ = 0
#@ ensures \result == 5
def f() -> int:
    d = {}
    d["a"] = 5
    return d["a"]
