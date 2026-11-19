"""Test statistics.median_high L5 — negative: caller can't discharge requires.

Documents the soundness path: a caller that does not establish the function's
precondition fails to verify under full proof.

(#49) gen #30 — IT DID NOT. This file used to carry `# pycsl-flags: --no-proof`,
`# pycsl-expected: PASS` and `#@ ensures True`, with a docstring saying the failure
mode was "exercised manually with `--proof`". Run that way it VERIFIED, because
`ensures True` is discharged by every program ever written. Sampling the family found
the same thing 60 times out of 60: not one `*_call_fails.py` witness fails, because not
one of them claims anything a program could contradict.

So this one now claims `\result == x` over a body returning `statistics.median_high(x)`
— an unresolved stdlib call the model cannot equate to `x` — with no `--no-proof` and
`# pycsl-expected: FAIL`. It fails under full proof, which is what the filename always
said it was for. `bin/check-claim-vacuity.py` counts the 1791 siblings still carrying a
contract that cannot fail.
"""
# pycsl-expected: FAIL
_ = 0  # anchor
import statistics  # noqa: F401


#@ ensures \result == x
def use_median_high_unsafe(x: int) -> int:
    return statistics.median_high(x)


if __name__ == "__main__":
    pass
