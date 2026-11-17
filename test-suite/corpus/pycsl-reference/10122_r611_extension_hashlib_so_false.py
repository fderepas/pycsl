r"""Test 10122 -- run #7 route #611 (expected FAIL): a `hashlib` EXTENSION module (`hashlib.cpython-314-x86_64-linux-gnu.so`) in an import root: CPython's FileFinder loads it before any source; pycsl took the stdlib digest model (rt62 r13: PROVED, CPython VIOLATION). REFUSED: PYCSL-SEM-IMPORT-NONSOURCE-ARTIFACT.
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r611art/ext
import hashlib


#@ ensures \result == True
#@ assigns \nothing
def same(s: str) -> bool:
    return hashlib.sha256(s.encode()).hexdigest() == hashlib.sha256(s.encode()).hexdigest()


if __name__ == "__main__":
    print(same("abc"))
