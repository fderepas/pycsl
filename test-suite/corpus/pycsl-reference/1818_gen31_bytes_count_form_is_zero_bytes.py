r"""Test 1818 — gen #31: `bytes(n)` is n ZERO bytes, and PyCSL now says so.

`bytes(n)` was left ill-typed on purpose (`bytes_new 2` against
`val bytes_new (x: array int)`), because at the time the ILL-TYPEDNESS was the only thing
stopping `b = bytes(2); b[0] = 7` from proving — see 1724/1725, which record that whole
episode. Route #217 then made `PYCSL-SEM-SUBSCRIPT` fire on a local bound from the
`bytes(...)` constructor, so the immutability line is held by a REFUSAL and no longer by an
accident. That was the precondition 1725's own note set for lifting the exclusion, and this
file is the payoff:

    b = bytes(2)
    return b[0]          # CPython: 0

lowers to `Array.make 2 0`, exactly as `bytearray(n)` already did, and proves.

CONTROLS AROUND IT, all run: 1819 is the FALSE twin (`== 1`) and must FAIL; 1725 still
FAILS, now by the refusal rather than by the type error; `bytes(-1)` FAILS (Why3's
`Array.make` needs `0 <= n`; CPython raises `ValueError: negative count`); `bytes(2)[5]`
FAILS (CPython raises IndexError). `len(bytes(3)) == 3` also FAILS — a PRE-EXISTING gap
shared with `bytearray`, measured rather than assumed, and NOT introduced here.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ ensures \result == 0
def f() -> int:
    b = bytes(2)
    return b[0]
