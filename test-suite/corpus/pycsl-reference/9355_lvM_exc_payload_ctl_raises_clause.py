r"""Test 9355 -- cap-exception-payload-model CONTROL (expected PASS): a `#@ raises E when C` contract on a USER
exception class emits the conditioned arm with the payload wildcard (`raises { NegErr _ -> x < 0 }`); a
bare `raise NegErr` (no argument) carries an unconstrained payload. CPython: f(2) == 2, f(-1) raises NegErr.
"""
# pycsl-expected: PASS


class NegErr(Exception):
    pass


#@ ensures \result == x
#@ raises NegErr when x < 0
#@ assigns \nothing
def f(x: int) -> int:
    if x < 0:
        raise NegErr
    return x


#@ ensures \result == 5 or \result == -1
#@ assigns \nothing
def g() -> int:
    try:
        return f(-1)
    except NegErr:
        return 5


if __name__ == "__main__":
    print("VIOLATION" if f(2) != 2 else "ok")
    print("VIOLATION" if g() not in (5, -1) else "ok")
