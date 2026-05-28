"""Test 0336 — PyCSL String length (cross-prover, tuesday-01).

The cross-prover bridge produces `\\str_length(s) + \\str_length(t)`
from the Coq/Lean `concat_length` fixtures. PyCSL's WhyML transpiler
currently treats `\\str_length` as a ghost-string operator that
doesn't apply directly to Python `str` parameters — `--no-proof`
exercises the parser + static semantics only.
"""
# pycsl-flags: --no-proof
#@ ensures \result == (\str_length(s) + \str_length(t))
#@ assigns \nothing
def concat_length(s: str, t: str) -> int:
    return len(s) + len(t)

if __name__ == "__main__":
    assert concat_length("hi", "there") == 7
    assert concat_length("", "") == 0
