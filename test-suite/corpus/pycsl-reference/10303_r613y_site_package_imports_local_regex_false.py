r"""Test 10303 -- run #8 u58, review rt69 G6 / n23d (FAIL, PRE-EXISTING). The program imports the installed
`lark`; lark/utils.py does `try: import regex`, which CPython resolves from sys.path BEFORE site-packages:
the --import-path root's (CPython: PYTHONPATH's) regex.py runs, rebinds `len` and raises ImportError, so
lark carries on and f() returns 7. The route #613 closure followed the stdlib and the startup hooks, never
third-party code: pycsl emitted (and PROVED) `\result == 3` at int72. REFUSED:
PYCSL-SEM-IMPORT-TRANSITIVE-SHADOW (program -> lark -> regex).
"""
# pycsl-expected: FAIL
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/r613y/g6
import lark


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return len("abc")


if __name__ == "__main__":
    print("result", f())
