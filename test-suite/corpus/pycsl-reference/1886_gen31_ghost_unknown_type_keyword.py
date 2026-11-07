r"""Test 1886 — gen #31 WITNESS (expected FAIL): a `#@ ghost` type keyword is checked.

The FIFTH member of the silent-name family, and the one that showed my own sweep phrase was
too narrow: `#@ ghost`'s second field is a type KEYWORD from a nine-entry table, not a NAME,
so "every directive whose grammar admits an identifier" did not reach it.

    #@ ghost g : no_such_type = 0
    let ghost g = ref 0 in
    [+] Verification SUCCESS! All contracts formally proven.

An unrecognised keyword was silently the `int` default, so a mistyped `ghost_dict` gave you
an int ghost and no message. §11's "untyped ghost declarations default to `int`" is what
made the silence look intentional: the DEFAULT is documented; the FALLBACK FROM A
MISSPELLED KEYWORD to that default is not.

Controls: 1887 (a real keyword) and 1889 (the UNTYPED form, which is `int` BY DESIGN and
must keep working — the refusal skips a `None` type for exactly that reason).
"""
# pycsl-expected: FAIL
_ = 0  # anchor


#@ requires x > 0
#@ ensures \result == x
#@ assigns \nothing
def f(x: int) -> int:
    #@ ghost g : no_such_type = 0
    return x
