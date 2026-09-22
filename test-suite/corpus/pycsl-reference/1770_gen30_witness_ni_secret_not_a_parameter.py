r"""Test 1770 — WITNESS: `noninterference secret <s>` where `s` is not a parameter.

The twin splits each SECRET parameter into an `_a`/`_b` pair and shares the public ones; a
secret that names no parameter splits nothing, so the twin's `assert ra == rb` would hold
trivially and certify a noninterference the policy never checked. Refused. One of the
refusals `bin/check-refusal-witness-coverage.py` measured as having no witness.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
#@ happy ni:
#@     targets summarize
#@     noninterference secret not_a_param
class Acct:
    #@ assigns \nothing
    #@ ensures \result == public_id * 2
    def summarize(self, public_id: int, balance: int) -> int:
        return public_id * 2
