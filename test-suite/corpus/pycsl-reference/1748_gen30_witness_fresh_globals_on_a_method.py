r"""Test 1748 — WITNESS for `PYCSL-SEM-FRESH-GLOBALS`: the directive on a METHOD.

`#@ fresh_globals` says a function starts from a fresh global state; a method's receiver
carries state that survives the call, so the combination is refused rather than
silently reinterpreted. One of the unwitnessed refusals measured by
`bin/check-refusal-witness-coverage.py`.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


class C:
    #@ fresh_globals
    #@ ensures \result == 0
    def m(self) -> int:
        return 0
