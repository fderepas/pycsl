r"""Test 3399 -- route #290 (expected PASS): CONTROL: a DIRECT element store on the named receiver is modelled and keeps PROVING (the pure immediately-applied lambda of route #115, 1313, stays emitted byte-identically).
"""
# pycsl-expected: PASS
from typing import List


#@ ensures \result == 39
def direct_store() -> int:
    xs: List[int] = [3, 1]
    xs[1] = 9
    return xs[0] * 10 + xs[1]



if __name__ == "__main__":
    assert direct_store() == 39
