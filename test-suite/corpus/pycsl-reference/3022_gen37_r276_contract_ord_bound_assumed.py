r"""Test 3022 — route #276 (expected PASS UNDER THE DECLARED MODEL ASSUMPTION LATIN1-STR).

Program: a CONTRACT-side `ord`: `requires len(s) == 1`, `ensures ord(s) < 256` (body inert). A Python `str` is modelled as a Why3 `string` of `string.Char`s, and Why3's
`axiom code` bounds every Char code by 256, so the claim PROVES; CPython REFUTES it (see
`__main__`). This is NOT a soundness bug of the default mode: it is the counterexample of the
declared assumption LATIN1-STR ("every str value consists of code points 0..255"), which
`pycsl --soundness-report` lists for this file and the reference docs state. Twin 3026 runs the
same program under `--strict-latin1`, where the assumption is dropped and the claim FAILS.
"""
# pycsl-model-assumption: LATIN1-STR
# pycsl-expected: PASS


#@ requires len(s) == 1
#@ ensures ord(s) < 256
#@ assigns \nothing
def f(s: str) -> int:
    return 0


if __name__ == "__main__":
    s = "\u20ac"
    print(f(s), ord(s) < 256)  # 0 False: the postcondition is FALSE for the euro sign
