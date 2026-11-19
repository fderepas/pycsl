r"""Test 10221 -- run #8 u55, review rt66 g02 (PASS control). Same declared mode as 10220, but
`r613x_g02c` exists only in the --import-path root, so CPython's order (test-suite/corpus first) and
pycsl's agree on the file: emitted exactly as at ff03f178c.
"""
# pycsl-expected: PASS
# pycsl-flags: --as-package-module test-suite/corpus --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r613x/g02
import r613x_g02c


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return r613x_g02c.one()


if __name__ == "__main__":
    print("result", f())
