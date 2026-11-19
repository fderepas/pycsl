r"""Test 6106 -- route #417 (expected FAIL): contract `"a\nb"` reached the model as backslash + n: `\result == "a\nb"` of `return "a\\nb"` (CPython False). PROVED at base 930d68ed5.
"""
# pycsl-expected: FAIL
#@ ensures \result == "a\nb"
#@ no_exception \all
def g() -> str:
    return "a\\nb"


if __name__ == "__main__":
    print(repr(g()), "claimed equal to 'a\\nb' (3 chars):", g() == "a\nb")
