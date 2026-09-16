r"""G29 A1 — WATCH auto_trust.py `_should_auto_trust_array_return`: an UNMARKED function returning
`List[int]` with an early return is force-trusted (body skipped, contract kept). Is a FALSE
postcondition then reported as verified?"""
from typing import List
_ = 0  # anchor


#@ requires n >= 0
#@ ensures \length(\result) == 1
#@ ensures \result[0] == 5
def mk(n: int) -> List[int]:
    if n > 100:
        return [7]
    return [1]


if __name__ == "__main__":
    print("CPython:", mk(3))
