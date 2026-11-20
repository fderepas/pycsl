r"""Test 10226 -- run #8 u55, review rt66 g01 (PASS control). `import zoneinfo` with no local file
named like a stdlib module: emitted exactly as at ff03f178c.
"""
# pycsl-expected: PASS
import zoneinfo


#@ ensures \result == 1
#@ assigns \nothing
def f() -> int:
    return 1


if __name__ == "__main__":
    print("result", f())
