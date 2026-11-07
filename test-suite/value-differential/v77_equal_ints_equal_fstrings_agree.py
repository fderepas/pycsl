"""v77 AGREE — two f-strings over the SAME value are the same string, and ROUTE #203's
value-keyed opaque keeps that provable.

The AGREE half is what tells #203's repair apart from a switch to `any`: `any` is fresh at
every evaluation, so it would still refuse v76 and would turn THIS red.
"""


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    n = 5
    a = f"{n}"
    b = f"{n}"
    if a == b:
        return 1
    return 2


if __name__ == "__main__":
    print(f())
