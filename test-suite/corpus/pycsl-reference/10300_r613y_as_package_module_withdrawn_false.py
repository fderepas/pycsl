r"""Test 10300 -- run #8 u58, review rt69 G1 / G2 / G3 / G4 (FAIL). `--as-package-module ROOT` is WITHDRAWN from
this release (route #613): passing it exits rc 2 before anything is verified, never a silent script-mode
verification. The shape is rt69 n13 / rt66 g02: under `python -m` from test-suite/corpus, `import r613x_g02`
loads test-suite/corpus/r613x_g02.py (returns 2), while pycsl's own order takes the --import-path copy
(returns 1); at int72 the program-FILE-NAME exemption of the g02 rule (G3) and the shallow parent `__init__`
judgement (G1) made such claims PROVE. REFUSED: rc 2 ("not supported in this release").
"""
# pycsl-expected: FAIL
# pycsl-flags: --as-package-module test-suite/corpus --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r613x/g02
import r613x_g02


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return r613x_g02.one()


if __name__ == "__main__":
    print("result", f())
