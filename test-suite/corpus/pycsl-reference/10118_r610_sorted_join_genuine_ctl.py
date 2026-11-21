r"""Test 10118 -- route #610 CONTROL (expected PASS): a GENUINE builtin `sorted` inside `",".join(sorted(xs))` (bound nowhere) keeps lvV's law-free model.
"""
# pycsl-expected: PASS
from __future__ import annotations
import hashlib
from typing import List


#@ ensures \result == True
#@ assigns \nothing
def keyed(xs: List[str]) -> bool:
    a = hashlib.sha256(",".join(sorted(xs)).encode()).hexdigest()
    return a == a


if __name__ == "__main__":
    print("result", keyed(["b", "a"]))
