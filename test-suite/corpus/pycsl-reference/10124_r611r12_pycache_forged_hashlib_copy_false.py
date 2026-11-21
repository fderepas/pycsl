r"""Test 10124 -- run #8 route #611 r12 (expected FAIL): a stdlib-identical LOCAL copy `hashlib.py` (admitted by route #326 as the interpreter's own source) with a FORGED unchecked-hash (PEP 552) `__pycache__/hashlib.cpython-314.pyc` (counter-based sha256) in an import root: CPython runs the cached bytecode WITHOUT reading the source (two digests differ, False), pycsl would reason about the source / the stdlib model. REFUSED: PYCSL-SEM-IMPORT-PYCACHE-UNVERIFIED.
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r611r12/hu
import hashlib


#@ ensures \result == True
#@ assigns \nothing
def same(s: str) -> bool:
    return hashlib.sha256(s.encode()).hexdigest() == hashlib.sha256(s.encode()).hexdigest()


if __name__ == "__main__":
    print(same("abc"))
