r"""Test 10120 -- run #7 route #611 (expected FAIL): a SOURCELESS `hashlib.pyc` (counter-based sha256) in an import root: CPython loads it, pycsl took the stdlib digest model and PROVED a two-digest equality (CPython False). REFUSED: PYCSL-SEM-IMPORT-NONSOURCE-ARTIFACT.
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r611art
import hashlib


#@ ensures \result == True
#@ assigns \nothing
def same(s: str) -> bool:
    return hashlib.sha256(s.encode()).hexdigest() == hashlib.sha256(s.encode()).hexdigest()


if __name__ == "__main__":
    print(same("abc"))
