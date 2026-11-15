r"""Test 10006 -- lvT generator-as-seq (expected FAIL): an INFINITE generator has no list of
yields (CPython's `list(ones("a"))` never returns; only a lazy `next()` gets an element), so the
eager lowering is sound only if the generator TERMINATES. Termination is a WhyML proof
obligation of the lowered body (no `\diverges`; the `while True` loop has no variant), so even an
impossible claim about the list must not be proved. Control: 10000, 10008.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import Iterator, List


#@ ensures len(\result) == len(\result) + 1
#@ assigns \nothing
#@ no_exception \all
def ones(k: str) -> Iterator[str]:
    while True:
        yield k


if __name__ == "__main__":
    for x in ones("a"):
        print("VIOLATION no list: lazily", x, "(list(ones('a')) never returns)")
        break
