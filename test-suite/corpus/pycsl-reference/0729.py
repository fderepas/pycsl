"""Test 0729 — HAPPY H-I2: noninterference via self-composition (positive).

`#@ happy ni: targets summarize noninterference secret balance` declares `balance` SECRET.
The meta-pass synthesizes a self-composition twin `summarize__selfcomp` that calls
`summarize` twice — public param `public_id` shared, secret `balance` split into
`balance_a`/`balance_b` — and asserts the two results are equal. Here `summarize`'s result
depends only on the public `public_id`, so the twin's `assert ra == rb` is provable: no leak.
This is exactly macsl's self-composition (../macsl src/macsl.ml emit_selfcomp), automated.
"""
# pycsl-flags: --memory-model hoare
#@ happy ni:
#@     targets summarize
#@     noninterference secret balance
class Acct:
    #@ requires True
    #@ ensures \result == public_id * 2
    def summarize(self, public_id: int, balance: int) -> int:
        return public_id * 2
