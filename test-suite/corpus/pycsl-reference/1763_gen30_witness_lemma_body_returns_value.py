r"""Test 1763 — WITNESS: a `#@ lemma` whose body RETURNS A VALUE.

`PYCSL-SEM-LEMMA`. A lemma is erased at extraction and its WhyML result is `unit`; the
body IS the proof, not a computation. A `return <expr>` in one would be silently dropped,
so it is refused and the message names the repair (`pass` for an immediate arm). One of
the refusals `bin/check-refusal-witness-coverage.py` measured as having no witness.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ lemma
#@ requires n >= 0
#@ ensures n + 0 == n
#@ assigns \nothing
def add_zero(n: int) -> None:
    return n
