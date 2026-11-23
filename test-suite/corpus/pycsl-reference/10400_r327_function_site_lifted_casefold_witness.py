r"""Test 10400 -- route #327, FUNCTION site (expected FAIL, refused): the live witness of the
PYCSL-R327-IDENT-COLLISION raise "the functions '...' and '...' lower to ONE WhyML identifier"
in src/pycsl/pycsl.py. Two nested `def f` (in `p` and in `q`) are lifted, and a module-level
`def F` folds to the same WhyML identifier `f`. Route #620 (PYCSL-SEM-WHYML-NAME-CLASH) leaves
a lifted-name collision to the later routes, so this program reaches the R327 function check.
Corpus 4307 (`def F` + `def f`) is refused earlier by #620 since run #9 u65 (red team rt77 F3);
this file replaces it as the witness of the R327 function site (run #9 u68).
"""
# pycsl-expected: FAIL


#@ ensures \result == 1
def p() -> int:
    def f() -> int:
        return 1
    return f()


#@ ensures \result == 2
def q() -> int:
    def f() -> int:
        return 2
    return f()


#@ ensures \result == 3
#@ assigns \nothing
def F() -> int:
    return 3


if __name__ == "__main__":
    assert p() == 1, p()
    assert q() == 2, q()
    assert F() == 3, F()
