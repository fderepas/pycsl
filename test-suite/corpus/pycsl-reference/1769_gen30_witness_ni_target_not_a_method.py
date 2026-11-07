r"""Test 1769 — WITNESS: `noninterference` targeting a method that does not exist.

The meta-pass synthesizes a self-composition twin for the NAMED method; with no such
method in any class of the module there is nothing to synthesize, and a policy that binds
to nothing would look like a proved noninterference claim while proving nothing. Refused.
One of the refusals `bin/check-refusal-witness-coverage.py` measured as having no witness.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
#@ happy ni:
#@     targets no_such_method
#@     noninterference secret balance
class Acct:
    #@ assigns \nothing
    #@ ensures \result == public_id * 2
    def summarize(self, public_id: int, balance: int) -> int:
        return public_id * 2
