r"""Test 10125 -- run #8 route #611 r12 (expected FAIL): a stdlib-identical LOCAL copy of the `tomllib` PACKAGE (its `.py` set and bytes equal the interpreter's, admitted by routes #326 / #611) whose SUBMODULE cache `__pycache__/_parser.cpython-314.pyc` is a FORGED unchecked-hash pyc (`loads` returns a fresh counter): CPython runs it (`tomllib.loads("a = 1")["a"]` is 1, then 2). Only the package-wide walk of an admitted copy reaches a submodule's cache (the rt62 j04 shape, with a cache instead of a sourceless pyc). REFUSED: PYCSL-SEM-IMPORT-PYCACHE-UNVERIFIED.
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r611r12/tu
import tomllib


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return 1


if __name__ == "__main__":
    a = tomllib.loads("a = 1")["a"]
    b = tomllib.loads("a = 1")["a"]
    print(a, b)
