r"""Test 6107 -- route #417 (expected FAIL): contract `"\n"` reached the model as backslash + n: `\result == "\n"` of `return "\\n"` (CPython False). PROVED at base 930d68ed5.
"""
# pycsl-expected: FAIL
#@ ensures \result == "\n"
#@ no_exception \all
def h() -> str:
    return "\\n"


if __name__ == "__main__":
    print(repr(h()), h() == "\n")
