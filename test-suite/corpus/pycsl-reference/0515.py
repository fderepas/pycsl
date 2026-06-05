"""Test 0515 — referential transparency: a pure @lru_cache is sound (no-more-int Stage F).

Memoizing a *referentially transparent* function — pure (`assigns \nothing`, no `\trusted` /
`\diverges`) and reading no mutable global — is sound: the cache is observationally transparent,
so the (uncached) body PyCSL verifies is consistent with the cached runtime. `square` is RT, and a
caller discharges the same postcondition over it. (Contracts go ABOVE the decorator.)"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor
from functools import lru_cache


#@ requires n >= 0
#@ ensures \result == n * n
#@ assigns \nothing
@lru_cache
def square(n: int) -> int:
    return n * n


#@ requires k >= 0
#@ ensures \result == k * k
def use_square(k: int) -> int:
    return square(k)
