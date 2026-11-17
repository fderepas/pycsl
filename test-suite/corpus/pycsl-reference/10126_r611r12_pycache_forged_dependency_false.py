r"""Test 10126 -- run #8 route #611 r12 (expected FAIL): a plain local DEPENDENCY `r611r12_dep.py` (`inc(x)` ensures `x + 1`) with a FORGED unchecked-hash `__pycache__/r611r12_dep.cpython-314.pyc` whose `inc` returns `x + 2`: CPython runs the cached bytecode (3), pycsl believes the source contract (2). REFUSED: PYCSL-SEM-IMPORT-PYCACHE-UNVERIFIED.
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r611r12/dep
import r611r12_dep


#@ ensures \result == 2
#@ assigns \nothing
def f() -> int:
    return r611r12_dep.inc(1)


if __name__ == "__main__":
    print(f())
