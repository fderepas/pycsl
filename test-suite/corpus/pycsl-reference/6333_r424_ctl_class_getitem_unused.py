r"""Test 6333 -- route #424 (expected PASS): CONTROL: a class defining `__class_getitem__` that is constructed and called but never subscripted; `{k}` of an instance under `no_exception \all` (CPython ok). PROVED at base and candidate.
"""
# pycsl-expected: PASS
class K:
    def __init__(self) -> None:
        self.n: int = 1

    def __class_getitem__(cls, item: int) -> int:
        return item


#@ no_exception \all
def f(k: K) -> int:
    s = {k}
    return len(s) + k.n


if __name__ == "__main__":
    print(f(K()))
