"""Test 0730 — negative: a result that depends on the SECRET leaks, caught by H-I2.

Same noninterference policy as 0729, but `summarize`'s result is `public_id + balance` — it
depends on the secret `balance`. The synthesized twin then has `ra = public_id + balance_a`,
`rb = public_id + balance_b`, and `assert ra == rb` is unprovable (the two secrets differ) —
the information leak surfaces as an unproven VC in `summarize__selfcomp`.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
#@ happy ni:
#@     targets summarize
#@     noninterference secret balance
class Acct:
    #@ requires True
    #@ ensures \result == public_id + balance
    def summarize(self, public_id: int, balance: int) -> int:
        return public_id + balance
