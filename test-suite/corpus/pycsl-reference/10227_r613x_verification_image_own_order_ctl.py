r"""Test 10227 -- run #8 u55 (PASS control): the DECLARED `--verification-image test-suite/corpus` (a
verification model CPython never executes; no CPython-run claim, listed by --soundness-report). The
program's own imports resolve as pycsl resolves them -- `multi_file_lib.r613x.g02.r613x_g02c` from the
program's directory -- so this is NOT refused, while the same file under `--as-package-module
test-suite/corpus` is (PACKAGE-MODE-ORDER: test-suite/corpus holds no `multi_file_lib`, so `python -m`
would not load that file).
"""
# pycsl-expected: PASS
# pycsl-flags: --verification-image test-suite/corpus
from multi_file_lib.r613x.g02.r613x_g02c import one


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return one()
