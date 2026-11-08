r"""Test 8128 -- route #517 (expected FAIL: REFUSED PYCSL-R517-TYPE-PARAM-NAME-READ): the def's own contract names its type parameter K as a value (`ensures \result == K`), which PyCSL folded to the module constant `K = 5`; inside the def K is a typing.TypeVar
"""
# pycsl-expected: FAIL

K = 5


#@ ensures \result == K
def f[K]() -> int:
    return 5


if __name__ == "__main__":
    print("result", f())
