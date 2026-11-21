"""Test 1093 — ROUTE #52 control: `x is x` is TRUE for every type and must keep proving.

TRUE OF THE PROGRAM: Python returns 0.

Identity is reflexive and the same name denotes the same object, so the same-variable shape
needs no type argument at all. Without this exemption the value-typed refusal takes a test
the model gets exactly right — measured while building it, which is why the exemption is
spelled before the type test rather than after.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ ensures \result == 0
#@ assigns \nothing
def f() -> int:
    a: str = "ab"
    if a is a:
        return 0
    return 7


if __name__ == "__main__":
    assert f() == 0
