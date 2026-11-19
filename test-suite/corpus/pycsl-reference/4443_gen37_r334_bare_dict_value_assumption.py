r"""Test 4443 -- gen #37 route #334 (expected PASS UNDER THE DECLARED MODEL ASSUMPTION BARE-CONTAINER-INT, now covering a bare `dict` / `Dict` / `Mapping`): a value of `d: dict` is read as an int, so `d["a"] % 1 == 0` PROVES although CPython refutes it for `{"a": 0.5}` (see `__main__`). The counterexample of the assumption, listed by `--soundness-report`; twin 4427 drops it (`--strict-bare-containers`).
"""
# pycsl-model-assumption: BARE-CONTAINER-INT
# pycsl-expected: PASS
#@ ensures \result == True
#@ assigns \nothing
def g(d: dict) -> bool:
    if "a" not in d:
        return True
    return d["a"] % 1 == 0

if __name__ == "__main__":
    print(g({"a": 0.5}))  # False: the proved claim is FALSE for a float value
