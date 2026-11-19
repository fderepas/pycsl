r"""Test 10227 -- run #8 u55 (PASS control): the DECLARED `--verification-image test-suite/corpus` (a
verification model CPython never executes; no CPython-run claim, listed by --soundness-report). The
program's own imports resolve as pycsl resolves them, so 10220's layout is NOT refused here: the -m order
rule does not apply to a file that is never run.
"""
# pycsl-expected: PASS
# pycsl-flags: --verification-image test-suite/corpus --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r613x/g02
import r613x_g02


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return r613x_g02.one()
