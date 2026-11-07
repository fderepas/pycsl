"""Test 1270 — route #96 CONTROL: the `\trusted` twin of 1269, and it agrees with it.

Identical to 1269 except `touch` is `\trusted`. Before the repair this file PROVED while 1269
FAILED — the whole route in one differential. After it, both FAIL, i.e. the bodyless val and the
verified body transmit the SAME frame. The pair is the standing equivalence witness.
"""
# pycsl-flags: --memory-model hoare
# pycsl-expected: FAIL

#@ requires \length(a) > 4
#@ assigns a[0..1]
#@ \trusted reviewer: route96
def touch(a: list) -> int:
    a[0] = 0
    return 0


#@ requires \length(arr) > 4
#@ requires arr[3] == 5
#@ ensures \result == 5
def driver(arr: list) -> int:
    touch(arr)
    return arr[3]
