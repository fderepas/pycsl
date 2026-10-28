r"""Test 6783 -- route #443 (expected PASS): CONTROL -- elements of `List[str]` / values of `Dict[str, str]` as method receivers are derived `str`; PROVED at base and candidate.
"""
# pycsl-expected: PASS
from typing import Dict, List


#@ no_exception \all
def f(xs: List[str], d: Dict[str, str]) -> int:
    if len(xs) == 0 or "a" not in d:
        return 0
    return len(xs[0].strip()) + len(d["a"].upper())


if __name__ == "__main__":
    print("result", f([" a "], {"a": "b"}))
