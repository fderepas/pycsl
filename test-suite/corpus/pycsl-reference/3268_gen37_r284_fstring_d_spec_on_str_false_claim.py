r"""Test 3268 — route #284 (expected FAIL): `f"{s:d}"` on a str under `no_exception \all` PROVED. CPython raises
`ValueError` (Unknown format code 'd' for object of type 'str') for every str.
"""
# pycsl-expected: FAIL


#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def f(s: str) -> int:
    t = f"{s:d}"
    return 1


if __name__ == "__main__":
    try:
        f("ab")
        raise SystemExit("unreachable")
    except ValueError:
        print("ValueError")
