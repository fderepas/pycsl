r"""Test 3788 -- gen #37 route #305 (expected PASS): control: a user SUBCLASS of the builtin (`class E(KeyError)`) raised and caught by `except E` must still PROVE; only a binding of the builtin NAME itself is refused.
"""
class E(KeyError):
    pass

#@ ensures \result == 1
def g(x: int) -> int:
    try:
        if x < 0:
            raise E("x")
    except E:
        return 1
    return 1

if __name__ == "__main__":
    assert g(-1) == 1
