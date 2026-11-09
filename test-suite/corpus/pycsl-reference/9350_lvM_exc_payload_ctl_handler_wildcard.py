r"""Test 9350 -- cap-exception-payload-model CONTROL (expected PASS): a USER exception class raised with a
string literal message is declared `exception BadInput string` and raised as `raise (BadInput <message>)`; the
handler arm binds the payload with a wildcard (`with BadInput _ ->`). The honest claim about the handler's
result proves. CPython: check(-3) == 1, check(4) == 0.
"""
# pycsl-expected: PASS


class BadInput(Exception):
    pass


#@ requires True
#@ ensures x < 0 ==> \result == 1
#@ ensures x >= 0 ==> \result == 0
#@ assigns \nothing
def check(x: int) -> int:
    try:
        if x < 0:
            raise BadInput("negative input")
        return 0
    except BadInput:
        return 1


if __name__ == "__main__":
    for v, want in ((-3, 1), (4, 0)):
        r = check(v)
        print("VIOLATION" if r != want else "ok", v, r)
