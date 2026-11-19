r"""Test 4405 -- gen #37 route #333 (control, expected PASS): control: user exceptions `_AErr` / `BErr` (distinct stripped tags) stay apart; the `_AErr` arm is taken. PROVED.
"""
# pycsl-expected: PASS
class _AErr(Exception):
    pass

class BErr(Exception):
    pass

#@ ensures \result == 2
#@ assigns \nothing
def g(n: int) -> int:
    try:
        raise _AErr()
    except BErr:
        return 1
    except _AErr:
        return 2
    return 0

if __name__ == "__main__":
    assert g(0) == 2, g(0)
