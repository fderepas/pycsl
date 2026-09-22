r"""Test 1739 — WITNESS: a `#@ happy ... targets <name>` whose target is not a method.

"A missing target is a hard error (a typo would silently attach the property to nothing)"
— the refusal's own words. Its sibling 1738 covers the same failure on the `except` side.
Both were written because `bin/check-refusal-witness-coverage.py` measured that 131 of the
compiler's 198 refusals still have no file proving they can fire.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
#@ happy availability:
#@     targets nosuchfn
#@     total
class Parser:
    #@ requires n >= 0
    #@ ensures \result >= 0
    def parse(self, n: int) -> int:
        return n
