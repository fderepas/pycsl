r"""Test 3269 — route #284 (expected FAIL): `"%q" % x` under `no_exception \all` PROVED for a BOUNDED x
(the `%` path had the same gap as the f-string spec; printed, so the string
types). CPython raises `ValueError` (unsupported format character 'q') for every operand: a literal
`%` format is now decided at emit time by CPython's own `%`, and an invalid one is owed as `false`.
"""
# pycsl-expected: FAIL


#@ requires 0 <= x and x <= 1000
#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def f(x: int) -> int:
    print("%q" % x)
    return 1


if __name__ == "__main__":
    try:
        f(5)
        raise SystemExit("unreachable")
    except ValueError:
        print("ValueError")
