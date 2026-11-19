r"""Test 10181 -- run #8 route #613 (FAIL): the program imports ONLY `hashlib`; the import root holds a local `_hashlib.py`. The stdlib `hashlib` does `import _hashlib` (the OpenSSL extension lives in lib-dynload, AFTER the root), so CPython loads the local file while pycsl keeps its sha-256 model. REFUSED: PYCSL-SEM-IMPORT-TRANSITIVE-SHADOW (program -> hashlib -> _hashlib).
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r613/hl
import hashlib


#@ ensures \result == True
#@ assigns \nothing
def same(s: str) -> bool:
    return hashlib.sha256(s.encode()).hexdigest() == hashlib.sha256(s.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    print("result", same("abc"))
