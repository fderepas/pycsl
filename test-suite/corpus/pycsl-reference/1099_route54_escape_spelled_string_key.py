"""Test 1099 — ROUTE #54 control: `"\\x61"` IS `"a"`, and the fold now agrees.

TRUE OF THE PROGRAM: Python's `len({"a": 10, "\\x61": 20})` is 1.

The int/bool witness (1095/1096) is the one everybody recognises; this is the one that says
the defect was never about `bool`. Two string keys that are EQUAL and spelled differently
were counted twice for the same reason — the fold compared source forms. FAILED at 967c68e1,
proves here.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    d = {"a": 10, "\x61": 20}
    return len(d)


if __name__ == "__main__":
    assert f() == 1
