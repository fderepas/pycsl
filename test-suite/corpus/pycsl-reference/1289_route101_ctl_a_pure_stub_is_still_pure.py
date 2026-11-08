# pycsl-flags: --memory-model hoare
# pycsl-expected: PASS
"""1289 — (#49) ROUTE #101 CAPABILITY ARM. The repair must not turn every bodyless `val`
into a havoc: a stub that honestly declares `#@ assigns \\nothing` is still PURE, and its
caller must still be able to prove the array unchanged across it.

This is the arm that would catch an over-broad repair — one that peeled write paths and then
framed things nobody writes. It PASSES on both sides of the change.

Must PASS.
"""


#@ \trusted reviewer: route101-ctl
#@ requires \length(g) > 0
#@ ensures \result == g[0]
#@ assigns \nothing
def peek(g: list) -> int:
    return g[0]


#@ requires \length(a) > 0
#@ requires a[0] == 7
#@ ensures \result == 7
def driver(a: list) -> int:
    x = peek(a)
    return a[0]
