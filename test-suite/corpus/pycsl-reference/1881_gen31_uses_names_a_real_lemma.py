r"""Test 1881 — gen #31 CONTROL for 1880 (expected PASS): a real citation still verifies.

Byte-identical to 1880 except that the cited name is the lemma that is actually there. The
refusal is about a name resolving to NOTHING, not a ban on `#@ uses` — the same control
discipline routes #13 and #223 pay for, and the reason the census mattered: all three
`#@ uses` sites in the tree (`0582` twice, `0565` once) cite a lemma in their own file, and
every one of them has to keep verifying.
"""
# pycsl-expected: PASS
_ = 0  # anchor


#@ lemma
#@ requires n >= 0
#@ ensures n + 0 == n
#@ assigns \nothing
def triv(n: int) -> None:
    pass


#@ uses triv
#@ ensures \result == 0
#@ assigns \nothing
def go() -> int:
    return 0
