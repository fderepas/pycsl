r"""Test 10301 -- run #8 u58, review rt69 (FAIL). The `--as-package-module=ROOT` spelling of the withdrawn mode
exits rc 2 too (rt69 n10b's shape: `python -m pkg` runs pkg/__main__.py, which pycsl never read). REFUSED: rc 2.
"""
# pycsl-expected: FAIL
# pycsl-flags: --as-package-module=test-suite/corpus


#@ ensures \result == 3
#@ assigns \nothing
def f() -> int:
    return len("abc")


if __name__ == "__main__":
    print("result", f())
