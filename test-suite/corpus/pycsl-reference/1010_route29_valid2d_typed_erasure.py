"""Test 1010 — ROUTE #29 PIN: `\valid2d` under `--memory-model typed`.

FALSE OF THE PROGRAM: `(500, 500)` is not a valid index of a 2x2 matrix.

A PIN, not a flip witness — see 1009 for why: `_handle_valid2d_expr` carries the
identical `if self._value_semantic: <formula>` / `return "true"` shape, and at
the parent commit c4233fed the file was masked by `unbound type symbol 'matrix'`
rather than by anything sound. The refusal
(`PYCSL-R29-HEAP-SPEC-ERASURE`) is what makes it fail-closed by design.
"""
# pycsl-flags: --memory-model typed
# pycsl-expected: FAIL
_ = 0  # anchor
#@ requires \length2d(mat, 2, 2)
#@ ensures \valid2d(mat, 500, 500)
#@ ensures \result == 0
def f(mat: list) -> int:
    return 0
