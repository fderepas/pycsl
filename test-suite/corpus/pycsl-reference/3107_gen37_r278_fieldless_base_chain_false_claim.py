r"""Test 3107 — route #278 (expected FAIL): a FIELDLESS base `A`, `B(A): pass`, `C(B)` overriding
`m` with `== 2` against `A.m`'s `== 1`. `merge_one` pairs `c__m` only with a `b__m` clone,
which a fieldless chain never gets, so no goal was built even under the flag. (The caller was
already fail-closed here — a fieldless class's method call is contract-free — so this file
is COVERAGE of the pair, not a reproduced false proof.) The MRO pair `c__m refines a__m` now
exists and its goal fails. CPython: 2.
"""
# pycsl-expected: FAIL


class A:
    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        return 1


class B(A):
    pass


class C(B):
    #@ ensures \result == 2
    #@ assigns \nothing
    def m(self) -> int:
        return 2


#@ ensures \result == 1
#@ assigns \nothing
def use(a: A) -> int:
    return a.m()


if __name__ == "__main__":
    print(use(C()))
    assert use(C()) == 2
