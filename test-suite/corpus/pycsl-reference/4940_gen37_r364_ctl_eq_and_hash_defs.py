r"""Test 4940 -- gen #37 route #364 (expected PASS): CONTROL: `__eq__` under `if` plus a top-level `def __hash__`: hashable, `{r}` proves (CPython ok).
"""
# pycsl-expected: PASS
class R:
    if True:
        def __eq__(self, o: object) -> bool:
            return True
    def __hash__(self) -> int:
        return 1

#@ no_exception \all
#@ ensures \result == 1
def g(r: R) -> int:
    s = {r}
    return 1

if __name__ == "__main__":
    print(g(R()))
