r"""Test 1755 — WITNESS: a TAB in `#@ act` block indentation.

The act-block parser requires spaces; a tab would make the block boundary depend on the
reader's tab width, so it is refused. One of the refusals
`bin/check-refusal-witness-coverage.py` measured as having no file proving it can fire.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ act small:
#@	given x < 0
#@	ensures \result == 1
#@ complete small
def f(x: int) -> int:
    return 1
