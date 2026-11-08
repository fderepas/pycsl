r"""Test 1783 — WITNESS: polymorphic recursion (GT4).

`PYCSL-TY3-GT4`. A generic function that calls itself with its OWN TypeVar does not
terminate under monomorphization: each specialization demands another. Refused loudly,
with the repair named (the recursive call must use a concrete type). One of the refusals
`bin/check-refusal-witness-coverage.py` measured as having no witness.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires n >= 0
#@ ensures \result >= 0
def depth[T](n: int) -> int:
    if n == 0:
        return 0
    return depth[T](n - 1)


#@ ensures \result >= 0
def use() -> int:
    return depth[int](0)
