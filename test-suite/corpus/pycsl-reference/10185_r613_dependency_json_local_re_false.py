r"""Test 10185 -- run #8 route #613 (FAIL): the program imports only a plain local dependency `r613_helper`, which imports `json`; the same root holds a local `re.py` (program -> r613_helper -> json -> re). REFUSED: PYCSL-SEM-IMPORT-TRANSITIVE-SHADOW.
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r613/dep
from r613_helper import one


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return one()


if __name__ == "__main__":
    print("result", f())
