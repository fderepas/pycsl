r"""Test 6121 -- route #417 (expected PASS): CONTROL: contract string literals without escapes keep their meaning under the decoding (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
#@ ensures \result == "plain"
#@ no_exception \all
def k() -> str:
    return "plain"


#@ ensures \result == "a b"
#@ no_exception \all
def m() -> str:
    return "a b"


if __name__ == "__main__":
    print(k(), m())
