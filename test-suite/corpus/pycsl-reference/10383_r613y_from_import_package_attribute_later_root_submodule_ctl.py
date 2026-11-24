r"""Test 10383 -- run #9 u66, review rt76 r14 control (PASS; u64's V2D refused it). The program's directory
(the corpus directory, sys.path[0]) holds a regular package zh80 whose __init__ defines b(); the later
--import-path root multi_file_lib/u66/B14 holds zh80/b.py. CPython stops at ./zh80 and `from zh80 import b`
takes its attribute, never importing a submodule: `cd <tree root> && PYTHONPATH=<B14> python <this file>`
prints "result 1".
"""
# pycsl-expected: PASS
# pycsl-flags: --import-path test-suite/corpus/pycsl-reference/multi_file_lib/u66/B14
from zh80 import b


#@ ensures \result == 1
#@ assigns \nothing
def g() -> int:
    return b()


if __name__ == "__main__":
    print("result", g())
