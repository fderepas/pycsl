r"""Test 3812 -- gen #37 route #306 (expected FAIL): module-constant str->str dict `OP_MAP.get("a", s[5])` under `no_exception \all`: the chained if-then-else put the default in the last `else`, but Python evaluates it eagerly (IndexError for s == ""). PROVED before #306.
"""
# pycsl-expected: FAIL
OP_MAP = {"a": "x", "b": "y"}


#@ no_exception \all
#@ ensures \result == "x"
def f(s: str) -> str:
    return OP_MAP.get("a", s[5])

if __name__ == "__main__":
    assert f("") == "x"
