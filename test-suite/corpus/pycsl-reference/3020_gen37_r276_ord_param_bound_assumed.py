r"""Test 3020 — route #276 (expected PASS UNDER THE DECLARED MODEL ASSUMPTION LATIN1-STR).

Program: a 1-char `str` parameter with `ensures \result < 256` over `return ord(s)`. A Python `str` is modelled as a Why3 `string` of `string.Char`s, and Why3's
`axiom code` bounds every Char code by 256, so the claim PROVES; CPython REFUTES it (see
`__main__`). This is NOT a soundness bug of the default mode: it is the counterexample of the
declared assumption LATIN1-STR ("every str value consists of code points 0..255"), which
`pycsl --soundness-report` lists for this file and the reference docs state. Twin 3024 runs the
same program under `--strict-latin1`, where the assumption is dropped and the claim FAILS.
"""
# pycsl-model-assumption: LATIN1-STR
# pycsl-expected: PASS


#@ requires len(s) == 1
#@ ensures \result < 256
#@ assigns \nothing
def f(s: str) -> int:
    return ord(s)


if __name__ == "__main__":
    print(f("a"), f("\u20ac"))  # 97 8364: the claim is FALSE for the euro sign
