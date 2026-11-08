r"""Test 3276 — route #285 (expected FAIL): `[chr(x) for x in xs]` under `no_exception \all` PROVED with `xs = [-1]`,
and CPython raises `ValueError`. The comprehension is lowered as an opaque value without per-element
obligations, so the refusal is now driven by `exception_model.TRIGGER_EXPR_SHAPES` (every TRIGGERS row).
"""
# pycsl-expected: FAIL

from typing import List


#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def f(xs: List[int]) -> int:
    cs = [chr(x) for x in xs]
    return 1


if __name__ == "__main__":
    try:
        f([-1])
        raise SystemExit("unreachable")
    except ValueError:
        print("ValueError")
