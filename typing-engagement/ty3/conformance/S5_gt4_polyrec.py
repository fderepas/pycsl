"""S5 STATIC gate — G6/GT4: polymorphic recursion is a LOUD-FAIL.

Per the two-plane spec §1.5: a generic function `f[T]` that calls `f[T]()`
(with the TypeVar itself) is polymorphic recursion — monomorphization does not
terminate. Must FAIL with PYCSL-TY3-GT4.
"""
_ = 0
def f[T]() -> None:
    f[T]()

if __name__ == "__main__":
    f[int]()
