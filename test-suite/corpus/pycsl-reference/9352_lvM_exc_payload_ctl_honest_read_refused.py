r"""Test 9352 -- cap-exception-payload-model CONTROL of 9351 (expected FAIL: refused PYCSL-R233-EXCEPT-AS-READ):
the HONEST claim about the same payload (`\result == "bang"`, CPython "bang") is refused too: the refusal
is a property of the read, not of the claim, so the payload model is not readable in either direction.
"""
# pycsl-expected: FAIL


class Oops(Exception):
    pass


#@ requires True
#@ ensures \result == "bang"
#@ assigns \nothing
def probe() -> str:
    try:
        raise Oops("bang")
    except Oops as e:
        return str(e)


if __name__ == "__main__":
    r = probe()
    print("VIOLATION contract" if r != "bang" else "ok", r)
