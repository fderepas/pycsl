r"""Test 10129 -- run #8 route #611 r12 over-refusal CONTROL (expected PASS): a stdlib-identical LOCAL copy of the `tomllib` PACKAGE (its `.py` set and bytes equal the interpreter's, admitted by routes #326 / #611) whose `__pycache__` holds GENUINE unchecked-hash caches of every module: each is provably the compilation of its source (code object == compile(source)), so the copy is admitted exactly as without a cache and the file proves.
"""
# pycsl-expected: PASS
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r611r12/tok
import tomllib


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return 1


if __name__ == "__main__":
    a = tomllib.loads("a = 1")["a"]
    b = tomllib.loads("a = 1")["a"]
    print(a, b)
