r"""Test 9351 -- cap-exception-payload-model (expected FAIL: refused PYCSL-R233-EXCEPT-AS-READ): the payload
is carried by the model but is NOT readable from Python. The claim `\result == "boom"` is FALSE of the
program (CPython returns "bang"); a read of the `except ... as e` binding stays refused (route #233), so the
false claim about the exception's payload can never prove. CPython: probe() == "bang".
"""
# pycsl-expected: FAIL


class Oops(Exception):
    pass


#@ ensures \result == "boom"
#@ assigns \nothing
def probe() -> str:
    try:
        raise Oops("bang")
    except Oops as e:
        return str(e)


if __name__ == "__main__":
    r = probe()
    print("VIOLATION contract" if r != "boom" else "ok", r)
