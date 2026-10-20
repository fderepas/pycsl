r"""Test 3358 -- route #293 (expected PASS): CONTROLS: the lexical `os.path` functions (`normpath`, `basename`, `dirname`, `join`) stay deterministic across `os.chdir` (CPython posixpath never reads the cwd for them).
"""
# pycsl-expected: PASS
import os


#@ ensures \result == 1
def f(s: str) -> int:
    a = os.path.normpath(s)
    b = os.path.basename(s)
    c = os.path.dirname(s)
    d = os.path.join(s, "x")
    os.chdir("/")
    a2 = os.path.normpath(s)
    b2 = os.path.basename(s)
    c2 = os.path.dirname(s)
    d2 = os.path.join(s, "x")
    #@ check a == a2
    #@ check b == b2
    #@ check c == c2
    #@ check d == d2
    return 1


if __name__ == "__main__":
    assert f("a/b") == 1
