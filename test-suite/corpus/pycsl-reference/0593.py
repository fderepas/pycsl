"""Test 0593 — `bytes` is the byte-buffer array class (0442.md B2, no-more-int).

A `bytes` parameter is `\valid`-able and indexable exactly like a `list`: it lowers to WhyML
`array int`, so `\valid(buf, 4)` (`Array.length buf >= 4`) and the element read `buf[i]` are
concrete array operations. A `-> bytes` return likewise lowers to `array int`. Before this fix
`bytes` collapsed to `int`: `\valid` rejected the param outright ("not a list parameter") and a
returned byte buffer was an untyped `int`. RED on the prior commit (pipeline error).
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ ensures \length(\result) == 2
#@ assigns \nothing
def pack2(v: int) -> bytes:
    return [v, v]


#@ requires \valid(buf, 4)
#@ requires 0 <= i and i < 4
#@ ensures \result == buf[i]
#@ assigns \nothing
def at(buf: bytes, i: int) -> int:
    return buf[i]
