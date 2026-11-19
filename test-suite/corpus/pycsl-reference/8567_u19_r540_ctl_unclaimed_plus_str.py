r"""Test 8567 -- route #540 (control, expected PASS): `+s` of a str in a function with NO `no_exception` claim (route #431 polarity: the raise only ends the function abnormally)
"""
# pycsl-expected: PASS
def f(s: str) -> int:
    +s
    return 1


if __name__ == "__main__":
    try:
        print("result", f("a"))
    except TypeError as e:
        print("raised (no claim)", e)
