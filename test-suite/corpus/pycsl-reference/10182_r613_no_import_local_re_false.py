r"""Test 10182 -- run #8 route #613 (FAIL): a program with NO import statement: `"a".encode("idna")` makes the codec registry import `encodings.idna`, which imports `re`; the local `re.py` in the root is that `re` (measured with CPython, witnesses-r613/n1). The builtins' C code imports modules pycsl cannot see, so the closure is never empty. REFUSED: PYCSL-SEM-IMPORT-TRANSITIVE-SHADOW (program -> builtins -> re).
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r613/re


#@ ensures \result == 1
#@ assigns \nothing
def one() -> int:
    return 1


if __name__ == "__main__":
    print("encoded", "a".encode("idna"))
    print("result", one())
