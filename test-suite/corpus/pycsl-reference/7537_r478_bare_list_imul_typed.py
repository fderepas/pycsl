r"""Test 7537 -- route #478 (expected FAIL): driver probe p15 under `--memory-model typed` -- the bare `list` annotation: `a *= 2; return len(a)` proved `\result == 2` at 8aaa864ca (CPython 4); now REFUSED (PYCSL-R478-COLLECTION-PARAM-AUGASSIGN).
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model typed
#@ requires \length(a) == 2
#@ ensures \result == 2
#@ assigns \nothing
def f(a: list) -> int:
    a *= 2
    return len(a)


if __name__ == "__main__":
    r = f([0, 0])
    if r != 2:
        print("VIOLATION contract", r)
