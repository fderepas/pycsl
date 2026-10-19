r"""Test 3119 — route #281 controls (PASS): a BOUNDED int converts under `no_exception \all`
(`str`, f-string, `!r`, `repr`, `print`, a mixed `print`); a HEX rendering `f"{x:x}"` owes
nothing (only decimal conversion is limited); a `no_exception KeyError` claim owes nothing
for a ValueError; and a function without `no_exception` is untouched.
"""
# pycsl-expected: PASS


#@ requires 0 <= x <= 1000
#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def f(x: int) -> int:
    s = str(x)
    t = f"v={x}"
    u = f"{x!r}"
    w = repr(x)
    print(x)
    print("a", x)
    return 1


#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def g(x: int) -> int:
    v = f"{x:x}"
    return 1


#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception KeyError
def h(x: int) -> int:
    s = str(x)
    return 1


#@ ensures \result == 1
#@ assigns \nothing
def k(x: int) -> int:
    s = str(x)
    return 1


if __name__ == "__main__":
    assert f(5) == 1 and g(10**5000) == 1 and k(3) == 1
    try:
        h(10**5000)
    except ValueError:
        print("h raises ValueError, outside its KeyError claim")
